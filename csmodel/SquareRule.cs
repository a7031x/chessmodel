using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csmodel
{
    using SquareRow = List<ChessState>;
    using States = List<List<int>>;

    struct ChessState
    {
        public int Piece;
        public int State;
    };

    class SquareRule
    {
        public static SquareRow[] SquareMap(string board)
        {
            var map = new SquareRow[90];
            for (int k = 0; k < 90; ++k)
                map[k] = new SquareRow();
            for (int k = 0; k < 90; ++k)
            {
                var piece = board[k];
                if (Move.Side(piece) == 0)
                    continue;
                map[k].Add(new ChessState { Piece = piece, State = 0 });
                var states = NextCovers(board, k);
                int state = 1;
                foreach(var s in states)
                {
                    foreach (var pos in s)
                        map[pos].Add(new ChessState { Piece = piece, State = state });
                    ++state;
                }
            }
		    return map;
        }

        private static States NextCovers(string board, int pos)
        {
            var piece = board[pos];
            switch (char.ToUpper(piece))
            {
                case 'R':
                    return NextRiderCovers(board, pos);
                case 'N':
                    return NextHorseCovers(board, pos);
                case 'B':
                    return NextElephantCovers(board, pos);
                case 'A':
                    return NextBishopCovers(board, pos);
                case 'K':
                    return NextKingCovers(board, pos);
                case 'C':
                    return NextCannonCovers(board, pos);
                case 'P':
                    return NextPawnCovers(board, pos);
                default:
                    throw new Exception("invalid piece");
            }
        }

        private static States NextRiderCovers(string board, int pos)
        {
            var covers = new List<int>();
            var next = new List<int>();
            int counter = 0;
            var (px, py) = Move.Position2(pos);
            bool check_add(int x, int y)
            {
                var p = Move.Position1(x, y);
                if (0 == counter)
                    covers.Add(p);
                else if (1 == counter)
                    next.Add(p);
                if (' ' != board[p])
                {
                    if (++counter == 2)
                        return false;
                }
                return true;
            };
            for (int x = px + 1; x < 9 && check_add(x, py); ++x) ;
            counter = 0;
            for (int x = px - 1; x >= 0 && check_add(x, py); --x) ;
            counter = 0;
            for (int y = py + 1; y < 10 && check_add(px, y); ++y) ;
            counter = 0;
            for (int y = py - 1; y >= 0 && check_add(px, y); --y) ;
            return new States{ covers, next };
        }

        private static States NextHorseCovers(string board, int pos)
        {
            var steps = new List<int>();
            var blocks = new List<int>();
            var next = new List<int>();
            var (px, py) = Move.Position2(pos);
            var dx = new []{ -2, -2, 2, 2, -1, -1, 1, 1 };
            var dy = new []{ -1, 1, -1, 1, -2, 2, -2, 2 };
            for (int k = 0; k < 8; ++k)
            {
                if (false == Move.ValidPosition(px + dx[k], py + dy[k]))
                    continue;
                var bx = dx[k] / 2;
                var by = dy[k] / 2;
                var block_position = Move.Position1(px + bx, py + by);
                var block = board[block_position] != ' ';
                var p = Move.Position1(px + dx[k], py + dy[k]);
                if (block)
                {
                    blocks.Add(block_position);
                    next.Add(p);
                }
                else
                    steps.Add(p);
            }
            return new States{ steps, blocks, next };
        }

        private static States NextElephantCovers(string board, int pos)
        {
            var steps = new List<int>();
            var blocks = new List<int>();
            var next = new List<int>();
            
            var (px, py) = Move.Position2(pos);
            var dx = new []{ -2, 2, -2, 2 };
            var dy = new []{ -2, -2, 2, 2 };
            var validy = new HashSet<int>{ 0, 2, 4, 5, 7, 9 };
            for (int k = 0; k < 4; ++k)
            {
                if (false == Move.ValidPosition(px + dx[k], py + dy[k]))
                    continue;
                if (false == validy.Contains(py + dy[k]))
                    continue;
                var bx = dx[k] / 2;
                var by = dy[k] / 2;
                var block_position = Move.Position1(px + bx, py + by);
                var block = board[block_position] != ' ';
                var p = Move.Position1(px + dx[k], py + dy[k]);
                if (block)
                {
                    blocks.Add(block_position);
                    next.Add(p);
                }
                else
                    steps.Add(p);
            }
            return new States{ steps, blocks, next };
        }

        private static States NextBishopCovers(string board, int pos)
        {
            var steps = new List<int>();
            var (px, py) = Move.Position2(pos);
            var dx = new []{ -1, 1, -1, 1 };
            var dy = new []{ -1, -1, 1, 1 };
            var validy = new HashSet<int>{ 0, 1, 2, 7, 8, 9 };
            for (int k = 0; k < 4; ++k)
            {
                if (false == Move.ValidPosition(px + dx[k], py + dy[k]))
                    continue;
                if (px + dx[k] < 3 || px + dx[k] > 5 || false == validy.Contains(py + dy[k]))
                    continue;
                var p = Move.Position1(px + dx[k], py + dy[k]);
                steps.Add(p);
            }
            return new States{ steps };
        }

        private static States NextKingCovers(string board, int pos)
        {
            var steps = new List<int>();
            var check = new List<int>();
            var (px, py) = Move.Position2(pos);
            var dx = new []{ -1, 1, 0, 0 };
            var dy = new []{ 0, 0, -1, 1 };
            var validy = new HashSet<int>{ 0, 1, 2, 7, 8, 9 };

            for (int k = 0; k < 4; ++k)
            {
                if (false == Move.ValidPosition(px + dx[k], py + dy[k]))
                    continue;
                if (px + dx[k] < 3 || px + dx[k] > 5 || false == validy.Contains(py + dy[k]))
                    continue;
                var p = Move.Position1(px + dx[k], py + dy[k]);
                steps.Add(p);
            }
            var inc = py <= 2 ? 1 : -1;
            for (int y = py + inc; y >= 0 && y < 10; y += inc)
            {
                var p = Move.Position1(px, y);
                if (' ' != board[p])
                {
                    if ('K' == char.ToUpper(board[p]))
                        steps.Add(p);
                    break;
                }
                else
                {
                    if (py <= 2 && y >= 7 || py >= 7 && y <= 2)
                        check.Add(p);
                }
            }
            return new States{ steps, check };
        }

        private static States NextCannonCovers(string board, int pos)
        {
            var steps = new List<int>();
            var next = new List<int>();
            var (px, py) = Move.Position2(pos);

            int counter = 0;
            bool checkAdd(int x, int y)
            {
                var p = Move.Position1(x, y);
                if (1 == counter)
                    steps.Add(p);
                else if (2 == counter)
                    next.Add(p);
                if (' ' != board[p])
                {
                    if (++counter == 3)
                        return false;
                }
                return true;
            };
            for (int x = px + 1; x < 9 && checkAdd(x, py); ++x) ;
            counter = 0;
            for (int x = px - 1; x >= 0 && checkAdd(x, py); --x) ;
            counter = 0;
            for (int y = py + 1; y < 10 && checkAdd(px, y); ++y) ;
            counter = 0;
            for (int y = py - 1; y >= 0 && checkAdd(px, y); --y) ;
            return new States{ steps, next };
        }

        private static States NextPawnCovers(string board, int pos)
        {
            var steps = new List<int>();
            var (px, py) = Move.Position2(pos);
            var dx = new []{ 0, -1, 1 };
            var dy = new []{ -1, 0, 0 };
            int reverse;
            int count;

            var redKingPos = (int)board.IndexOf('K');
            if (Move.IsRed(board[pos]) == (redKingPos >= 45))
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
                if (false == Move.ValidPosition(px + dx[k], py + dy[k] * reverse))
                    continue;
                var p = Move.Position1(px + dx[k], py + dy[k] * reverse);
                steps.Add(p);
            }
            return new States{ steps };
        }
    }
}
