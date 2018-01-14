using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csmodel
{
    class Rule
    {
        public static int Base = 100;
        public static int GameOverThreshold = 150 * Base;
        private static IDictionary<char, int> scoreMap = new Dictionary<char, int>
        {
            {'R', 10 }, {'N', 4}, {'B', 1}, {'A', 1}, {'K', 300}, {'C', 4}, {'P', 1},
            {'r', -10 }, {'n', -4}, {'b', -1}, {'a', -1}, {'k', -300}, {'c', -4}, {'p', -1},
            {' ', 0 }
        };

        public static int BasicScore(string board)
        {
            return board.Sum(x => scoreMap[x]) * Base;
        }

        public static char FlipSide(char piece)
        {
            return char.IsUpper(piece) ? char.ToLower(piece) : char.ToUpper(piece);
        }

        public static string FlipSide(string board)
        {
            board = new string(board.Select(Rule.FlipSide).ToArray());
            return board;
        }

        public static string RotateBoard(string board)
        {
            var array = board.ToCharArray();
            Array.Reverse(array);
            return new string(array);
        }

        internal static char[] SquareTypes()
        {
            return new[] { 'R', 'N', 'B', 'A', 'K', 'C', 'P', 'r', 'n', 'b', 'a', 'k', 'c', 'p', ' ' };
        }
    }

    class Move
    {
        private static readonly int[] horseDx = { -2, -2, 2, 2, -1, -1, 1, 1 };
        private static readonly int[] horseDy = { -1, 1, -1, 1, -2, 2, -2, 2 };
        private static readonly int[] elephantDx = { -2, 2, -2, 2 };
        private static readonly int[] elephantDy = { -2, -2, 2, 2 };
        private static readonly int[] bishopDx = { -1, 1, -1, 1 };
        private static readonly int[] bishopDy = { -1, -1, 1, 1 };
        private static readonly int[] kingDx = { -1, 1, 0, 0 };
        private static readonly int[] kingDy = { 0, 0, -1, 1 };

        public static string NextBoard(string board, Tuple<int, int> move)
        {
            var r = board.ToCharArray();
            r[move.Item2] = r[move.Item1];
            r[move.Item1] = ' ';
            return new string(r);
        }

        public static IList<Tuple<int, int>> NextSteps(string board, bool red)
        {
            var steps = new List<Tuple<int, int>>();
            for(int k = 0; k < board.Length; ++k)
            {
                var piece = board[k];
                if (Side(piece) == 0 || IsRed(piece) != red)
                    continue;
                IEnumerable<int> moves;
                switch(char.ToUpper(piece))
                {
                    case 'R':
                        moves = RiderSteps(board, k);
                        break;
                    case 'N':
                        moves = HorseSteps(board, k);
                        break;
                    case 'B':
                        moves = ElephantSteps(board, k);
                        break;
                    case 'A':
                        moves = BishopSteps(board, k);
                        break;
                    case 'K':
                        moves = KingSteps(board, k);
                        break;
                    case 'C':
                        moves = CannonSteps(board, k);
                        break;
                    case 'P':
                        moves = PawnSteps(board, k);
                        break;
                    default:
                        throw new Exception("invalid piece");
                }
                foreach (var move in moves)
                    steps.Add(Tuple.Create(k, move));
            }
            return steps;
        }

        private static IEnumerable<int> RiderSteps(string board, int pos)
        {
            var steps = new List<int>();
            var (px, py) = Position2(pos);
            bool checkAdd(int x, int y)
            {
                var p = Position1(x, y);
                if (Side(board[p]) * Side(board[pos]) <= 0)
                    steps.Add(p);
                return ' ' == board[p];
            }

            for (int x = px + 1; x < 9 && checkAdd(x, py); ++x);
            for (int x = px - 1; x >= 0 && checkAdd(x, py); --x);
            for (int y = py + 1; y < 10 && checkAdd(px, y); ++y);
            for (int y = py - 1; y >= 0 && checkAdd(px, y); --y);
            return steps;
        }

        private static IEnumerable<int> HorseSteps(string board, int pos)
        {
            var steps = new List<int>();
            var (px, py) = Position2(pos);
            for(int k = 0; k < 8; ++k)
            {
                if (false == ValidPosition(px + horseDx[k], py + horseDy[k]))
                    continue;
                var bx = horseDx[k] / 2;
                var by = horseDy[k] / 2;
                if (board[Position1(px + bx, py + by)] != ' ')
                    continue;
                var p = Position1(px + horseDx[k], py + horseDy[k]);
                if (Side(board[p]) * Side(board[pos]) <= 0)
                    steps.Add(p);
            }
            return steps;
        }

        private static IEnumerable<int> CannonSteps(string board, int pos)
        {
            var steps = new List<int>();
            var (px, py) = Position2(pos);
            int counter = 0;
            bool checkAdd(int x, int y)
            {
                var p = Position1(x, y);
                switch (counter)
                {
                    case 0:
                        if (' ' == board[p])
                            steps.Add(p);
                        else
                            ++counter;
                        return true;
                    case 1:
                        if (Side(board[p]) * Side(board[pos]) < 0)
                            steps.Add(p);
                        if (' ' != board[p])
                            ++counter;
                        return 1 == counter;
                    default:
                        return false;
                }
            }
            for (int x = px + 1; x < 9 && checkAdd(x, py); ++x) ;
            counter = 0;
            for (int x = px - 1; x >= 0 && checkAdd(x, py); --x) ;
            counter = 0;
            for (int y = py + 1; y < 10 && checkAdd(px, y); ++y) ;
            counter = 0;
            for (int y = py - 1; y >= 0 && checkAdd(px, y); --y) ;
            return steps;
        }

        public static IEnumerable<int> ElephantSteps(string board, int pos)
        {
            var steps = new List<int>();
            var (px, py) = Position2(pos);
            var validy = new HashSet<int> { 0, 2, 4, 5, 7, 9 };
            for (int k = 0; k < 4; ++k)
            {
                if (false == ValidPosition(px + elephantDx[k], py + elephantDy[k]))
                    continue;
                var bx = elephantDx[k] / 2;
                var by = elephantDy[k] / 2;
                if (board[Position1(px + bx, py + by)] != ' ')
                    continue;
                if (false == validy.Contains(py + elephantDy[k]))
                    continue;
                var p = Position1(px + elephantDx[k], py + elephantDy[k]);
                if (Side(board[p]) * Side(board[pos]) <= 0)
                    steps.Add(p);
            }
            return steps;
        }

        private static IEnumerable<int> BishopSteps(string board, int pos)
        {
            var steps = new List<int>();
            var (px, py) = Position2(pos);
            var validy = new HashSet<int> { 0, 1, 2, 7, 8, 9 };
            for(int k = 0; k < 4; ++k)
            {
                if (false == ValidPosition(px + bishopDx[k], py + bishopDy[k]))
                    continue;
                if (px + bishopDx[k] < 3 || px + bishopDx[k] > 5 || false == validy.Contains(py + bishopDy[k]))
                    continue;
                var p = Position1(px + bishopDx[k], py + bishopDy[k]);
                if (Side(board[p]) * Side(board[pos]) <= 0)
                    steps.Add(p);
            }
            return steps;
        }

        private static IEnumerable<int> KingSteps(string board, int pos)
        {
            var steps = new List<int>();
            var (px, py) = Position2(pos);
            var validy = new HashSet<int> { 0, 1, 2, 7, 8, 9 };

            for (int k = 0; k < 4; ++k)
            {
                if (false == ValidPosition(px + kingDx[k], py + kingDy[k]))
                    continue;
                if (px + kingDx[k] < 3 || px + kingDx[k] > 5 || false == validy.Contains(py + kingDy[k]))
                    continue;
                var p = Position1(px + kingDx[k], py + kingDy[k]);
                if (Side(board[p]) * Side(board[pos]) <= 0)
                    steps.Add(p);
            }
            var inc = py <= 2 ? 1 : -1;
            for (int y = py + inc; y >= 0 && y < 10; y += inc)
            {
                var p = Position1(px, y);
                if (' ' != board[p])
                {
                    if ('K' == char.ToUpper(board[p]))
                        steps.Add(p);
                    break;
                }
            }
            return steps;
        }

        private static IEnumerable<int> PawnSteps(string board, int pos)
        {
            var steps = new List<int>();
            var (px, py) = Position2(pos);
            var dx = new[] { 0, -1, 1 };
            var dy = new[] { -1, 0, 0 };

            int reverse;
            int count;
            var redKingPos = (int)board.IndexOf('K');
            if (IsRed(board[pos]) == (redKingPos >= 45))
            {
                if (py <= 4)
                    count = 3;
                else
                    count = 1;
                reverse = 1;
            }
            else
            {
                if (py >= 5)
                    count = 3;
                else
                    count = 1;
                reverse = -1;
            }

            for (int k = 0; k < count; ++k)
            {
                if (false == ValidPosition(px + dx[k], py + dy[k] * reverse))
                    continue;
                var p = Position1(px + dx[k], py + dy[k] * reverse);
                if (Side(board[p]) * Side(board[pos]) <= 0)
                    steps.Add(p);
            }
            return steps;
        }

        public static bool IsRed(char piece)
        {
            return 'A' <= piece && 'Z' >= piece;
        }

        public static int Side(char piece)
        {
            if(IsRed(piece))
                return 1;
            else if(' ' == piece)
                return 0;
            else
                return -1;
        }
        public static int Position1(int x, int y)
        {
            return x + y * 9;
        }

        public static (int, int) Position2(int pos)
        {
            return (pos % 9, pos / 9);
        }

        public static bool ValidPosition(int x, int y)
        {
            return x >= 0 && x < 9 && y >= 0 && y < 10;
        }
    }
}
