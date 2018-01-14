using System.Collections.Generic;
using System.Linq;

namespace csmodel
{
    using SquareRow = List<ChessState>;
    class Feeder
    {
        private static Dictionary<int, int> c2t = new Dictionary<int, int>
        {
            {'R', 0 }, {'N', 1}, {'B', 2}, {'A', 3}, {'K', 4}, {'C', 5}, {'P', 6},
            {'r', 7 }, {'n', 8}, {'b', 9}, {'a', 10}, {'k', 11}, {'c', 12}, {'p', 13},
            {' ', 14 }
        };

        public static string NormalBoard(string board, bool red)
        {
            if (false == red)
                board = Rule.FlipSide(board);
            var pos = board.IndexOf('K');
            if (pos < 45)
                board = Rule.RotateBoard(board);
            return board;
        }

        private static void FillFeedRow(SquareRow row, int mlen)
        {
            while (row.Count < mlen)
                row.Add(new ChessState { Piece = ' ', State = 0 });
        }

        public static (int[], int[], float[]) Feed(IEnumerable<string> boards, bool red)
        {
            boards = boards.Select(board => NormalBoard(board, red)).ToArray();
            var maps = boards.Select(board => SquareRule.SquareMap(board)).ToArray();
            var scores = boards.Select(board => (float)Rule.BasicScore(board)).ToArray();
            var lenths = maps.SelectMany(map => map.Select(row => row.Count)).ToArray();
            var mlen = lenths.Max();
            foreach(var map in maps)
            {
                foreach(var row in map)
                    FillFeedRow(row, mlen);
            }
            var squares = maps.SelectMany(map => map.SelectMany(row => row.SelectMany(cs => new[] { c2t[cs.Piece], cs.State }))).ToArray();
            return (squares, lenths, scores);
        }
    }
}
