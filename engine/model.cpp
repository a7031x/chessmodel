#include "model.h"
#include <tensorflow/cc/client/client_session.h>
#include <tensorflow/cc/ops/standard_ops.h>
#include <tensorflow/core/framework/tensor.h>

model_t::model_t()
{
	_session = std::make_shared<ClientSession>();

}

std::vector<float> model_t::predict(const std::vector<std::string> &boards, bool red)
{

}