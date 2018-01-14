using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csmodel
{
    public class SearchEngine
    {
        private Model _model;
        private Dictionary<long, HashItem> _hash;
        private List<Dictionary<char, long>> _hash_table;

        class HashItem
        {
            public int Depth;
            public float Score;
            public Tuple<int, int> Move;
        };

        public class SearchItem
        {
            public string Board;
            public Tuple<int, int> Move;
            public float Score;
        };

	    public SearchEngine(Model model)
        {
            _model = model;
            _hash = new Dictionary<long, HashItem>();
            _hash_table = new List<Dictionary<char, long>>();
            Load();
        }

        public List<SearchItem> Search(string board, bool red, int depth)
	    {
            var r = new List<SearchItem>();
            DeepSearch(r, depth, board, red, depth, 0, -Rule.GameOverThreshold * 3, Rule.GameOverThreshold * 3);
            r = r.OrderBy(x => red ? -x.Score : x.Score).ToList();
            return r;
	    }

	    private float DeepSearch(List<SearchItem> pack,
            int org_depth, string board, bool red,
            int depth, int captured, float minscore, float maxscore)
        {
            var key = ComputeHash(board, red);
            var hash = FindHash(key);
            if (hash != null && hash.Depth >= depth)
            {
                if (depth == org_depth)
                    FillMoves(pack, board, hash.Move, hash.Score, red);
                return hash.Score;
            }

            var moves = Move.NextSteps(board, red);
            var next_boards = new List<string>();
            var next_scores = new List<float>();

            Tuple<int, int> best_move = Tuple.Create(0, 0);
            float best_score = red ? -Rule.GameOverThreshold * 3 : Rule.GameOverThreshold * 3;

            foreach (var move in moves)
            {
                var next_board = Move.NextBoard(board, move);
                var next_score = Rule.BasicScore(next_board);
                if (red && next_score > best_score || !red && next_score < best_score)
                {
                    best_move = move;
                    best_score = next_score;
                }
                next_boards.Add(next_board);
                next_scores.Add(next_score);
            }
            if (Math.Abs(best_score) < Rule.GameOverThreshold && depth + captured == 1)
            {
                next_scores = _model.Predict(next_boards, !red).ToList();
                best_score = red ? -Rule.GameOverThreshold * 3 : Rule.GameOverThreshold * 3;
                for (int k = 0; k < moves.Count; ++k)
                {
                    var move = moves[k];
                    var score = next_scores[k];
                    if (red && score > best_score || !red && score < best_score)
                    {
                        best_move = move;
                        best_score = score;
                    }
                }
            }
            if (1 >= depth + captured || Math.Abs(best_score) >= Rule.GameOverThreshold)
            {
                if (Math.Abs(best_score) >= Rule.GameOverThreshold)
                {
                    if (best_score < 0)
                        best_score -= depth;
                    else
                        best_score += depth;
                }
                if (depth == org_depth)
                    FillMoves(pack, board, best_move, best_score, red);
                SaveHash(key, depth, best_score, best_move);
                return best_score;
            }
            var idx = new int[next_scores.Count];
            for (int k = 0; k < idx.Length; ++k)
                idx[k] = k;

            idx = idx.OrderBy(x => red ? -next_scores[x] : next_scores[x]).ToArray();
            best_score = red ? -Rule.GameOverThreshold * 3 : Rule.GameOverThreshold * 3;
            foreach (var index in idx)
            {
                var move = moves[index];
                var captive = new[] { 'R', 'r', 'H', 'h', 'C', 'c' }.Contains(board[move.Item2]) ? 1 : 0;
                var next_board = next_boards[index];
                var next_score = DeepSearch(pack, org_depth, next_board, !red, depth - 1, Math.Min(captured + captive, 0), minscore, maxscore);
                if (red && next_score > best_score || !red && next_score < best_score)
                {
                    best_score = next_score;
                    best_move = move;
                }
                if (red)
                {
                    if (next_score >= maxscore)
                        break;
                    else if (minscore < next_score)
                        minscore = next_score;
                }
                else
                {
                    if (next_score <= minscore)
                        break;
                    else if (maxscore > next_score)
                        maxscore = next_score;
                }
                if (depth == org_depth)
                    pack.Add(new SearchItem{ Board = board, Move = move, Score = next_score });
            }
            SaveHash(key, depth, best_score, best_move);
            return best_score;
	    }

	    void Load()
        {
            var types = Rule.SquareTypes();
            var rand = new Random();
            for (var k = 0; k < 90; ++k)
            {
                var table = new Dictionary<char, long>();
                foreach (var type in types)
                {
                    table.Add(type, (rand.Next() << 32) | rand.Next());
                }
                _hash_table.Add(table);
            }
        }

        long ComputeHash(string board, bool red)
        {
            long hash = red ? 0 : -1;
            for (int k = 0; k < 90; ++k)
            {
                var table = _hash_table[k];
                hash ^= table[board[k]];
            }
            return hash;
        }

        HashItem FindHash(long key)
        {
            _hash.TryGetValue(key, out HashItem value);
            return value;
        }

        void SaveHash(long key, int depth, float score, Tuple<int, int> move)
        {
            var hash = new HashItem { Depth = depth, Score = score, Move = move };
            if (_hash.ContainsKey(key))
                _hash[key] = hash;
            else
                _hash.Add(key, hash);
        }

        void FillMoves(List<SearchItem> pack, string board, Tuple<int, int> move, float score, bool red)
        {
            if (pack.Any())
                return;
            var moves = Move.NextSteps(board, red);
            var index = moves.IndexOf(move);
            moves[index] = moves[0];
            moves[0] = move;
            var boards = moves.Select(m => Move.NextBoard(board, m));
            var scores = _model.Predict(boards, !red);

            foreach(var (b, m, s) in boards.Zip(moves, (b, m) => (b, m)).Zip(scores, (c, s) => (c.Item1, c.Item2, s)))
            {
                pack.Add(new SearchItem{ Board = b, Move = m, Score = s});
            }
        }
    }
}
