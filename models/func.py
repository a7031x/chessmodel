import torch
import torch.nn as nn
import utils

FORCE_CPU = False


def tensor(v):
    if isinstance(v, torch.Tensor):
        return v.cuda() if gpu_available() else v
    else:
        return torch.tensor(v).cuda() if gpu_available() else torch.tensor(v)


def zeros(*kwargs):
    v = torch.zeros(kwargs)
    return tensor(v)


def ones(*kwargs):
    v = torch.ones(kwargs)
    return tensor(v)


def full(*args, **kwargs):
    v = torch.full(*args, **kwargs)
    return tensor(v)


def randn(*args, **kwargs):
    v = torch.randn(*args, **kwargs)
    return tensor(v)


def sequence_mask(lengths, max_len=None):
    batch_size = lengths.numel()
    max_len = max_len or lengths.max()
    return (
        torch.arange(0, max_len)
        .type_as(lengths)
        .repeat(batch_size, 1)
        .lt(lengths.unsqueeze(1))
    )


def pad_zeros(value, full_size, dim=0):
    if full_size == value.shape[dim]:
        return value
    padding = [0] * (value.dim() * 2)
    padding[-dim * 2 - 1] = full_size - value.shape[dim]
    padded_value = nn.functional.pad(value, padding)
    return padded_value


def softmax_mask(val, mask):
    return -1e18 * (1 - mask.float()) + val


def onehot(val, dim):
    shape = list(val.shape) + [dim]
    onehot = zeros(*shape).scatter_(-1, val.unsqueeze(-1), 1)
    return onehot


def gpu_available():
    return torch.cuda.is_available() if not FORCE_CPU else False


def use_last_gpu():
    device = torch.cuda.device_count() - 1
    use_gpu(device)


def use_gpu(device):
    if device == -1:
        use_cpu()
    else:
        global FORCE_CPU
        FORCE_CPU = False
        max_device = torch.cuda.device_count() - 1
        if device > max_device:
            return
        torch.cuda.set_device(device)


def use_cpu():
    global FORCE_CPU
    FORCE_CPU = True


def cuda(module):
    return module.cuda() if gpu_available() else module


def load_checkpoint(path):
    return torch.load(path, map_location=lambda storage, location: storage)


def multinomial(x, padding_ids, best_in_k=1):
    _, mids = x.max(-1)
    pad_mask = 0
    for padding_id in padding_ids:
        pad_mask += (mids == padding_id).long()
    if 1 == best_in_k:
        x = x.multinomial(1).squeeze(1)
    else:
        ids = x.multinomial(best_in_k, replacement=False)
        x = x.gather(-1, ids)
        _, m = x.max(-1)
        x = ids.gather(-1, m.unsqueeze(1)).squeeze(-1)
    x = x * (1 - pad_mask) + padding_id * pad_mask
    return x


def align1d(value, mlen, fill=0):
    if torch.is_tensor(value):
        if not torch.is_tensor(fill):
            fill = torch.tensor(fill, dtype=value.dtype, device=value.device)
        return torch.cat([value] + [fill.unsqueeze(dim=0)] * (mlen - len(value)))
    else:
        return list(value) + [fill] * (mlen - len(value))


def align2d(values, fill=0):
    mlen = max([len(row) for row in values])
    return [align1d(row, mlen, fill) for row in values]


def align3d(values, fill=0):
    lengths = [[len(x) for x in y] for y in values]
    maxlen0 = max([max(x) for x in lengths])
    maxlen1 = max([len(x) for x in lengths])
    for row in values:
        for line in row:
            line += [fill] * (maxlen0 - len(line))
        row += [([fill] * maxlen0)] * (maxlen1 - len(row))
    return values


def eval_dim(values):
    dim = 0
    inp = values
    while (
        isinstance(inp, list)
        or isinstance(inp, tuple)
        or (isinstance(inp, torch.Tensor) and inp.dim() > 0)
    ):
        dim += 1
        if 0 == len(inp):
            return dim
        inp = inp[0]
    return dim


def align(values, fill=0):
    dim = 0
    values = list(values)
    dim = eval_dim(values) - eval_dim(fill)
    if dim == 1:
        return values
    elif dim == 2:
        return align2d(values, fill)
    elif dim == 3:
        return align3d(values, fill)
    else:
        raise NotImplementedError()


def chunk(values, size, overlap=0):
    if not isinstance(values, list):
        values = list(values)
    for i in range(0, len(values) - overlap, size - overlap):
        yield values[i: i + size]


def trace(x, access):
    q = [e for e in x]
    visited = set(q)
    while q:
        e = q.pop(0)
        access(e)
        for c in e.children:
            if c not in visited:
                visited.add(c)
                q.append(c)


def flatten(l2):
    return [item for l1 in l2 for item in l1]


def save_model(model, ckpt_path):
    utils.ensure_folder(ckpt_path)
    ckpt = {
        "model": model.state_dict(),
    }
    torch.save(ckpt, ckpt_path)


def load_model(model, ckpt_path):
    ckpt = load_checkpoint(ckpt_path)
    model.load_state_dict(ckpt['model'])
