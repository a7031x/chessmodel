using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UI
{
    public class Utility
    {
        public static String TransformBoard(byte[] board, char empty = '#')
        {
            var r = string.Empty;
            foreach (var c in board)
                r += TransformChess(c, empty);
            return r;
        }

        public static char TransformChess(byte chess, char empty)
        {
            switch (chess)
            {
                case 256 - 6: return 'r';
                case 256 - 2: return 'n';
                case 256 - 5: return 'b';
                case 256 - 4: return 'a';
                case 256 - 3: return 'k';
                case 256 - 7: return 'c';
                case 256 - 1: return 'p';
                case 6: return 'R';
                case 2: return 'N';
                case 5: return 'B';
                case 4: return 'A';
                case 3: return 'K';
                case 7: return 'C';
                case 1: return 'P';
                default: return empty;
            }
        }

        public static void RotateBoard(byte[] board)
        {
            for (int k = 0; k < 45; ++k)
            {
                var b = board[k];
                board[k] = board[89 - k];
                board[89 - k] = b;
            }
        }

        public static void FlipBoard(byte[] board)
        {
            for (int row = 0; row < 10; ++row)
            {
                for (int column = 0; column < 4; ++column)
                {
                    var b = board[row * 9 + column];
                    board[row * 9 + column] = board[row * 9 + 8 - column];
                    board[row * 9 + 8 - column] = b;
                }
            }
        }
        public static int FlipIndex(int index)
        {
            var column = index % 9;
            return index + 8 - 2 * column;
        }
        public static int RotateIndex(int index)
        {
            return 89 - index;
        }
        public static void IndexToPosition(int index, out int column, out int row)
        {
            column = index % 9;
            row = index / 9;
        }
        public static int PositionToIndex(int column, int row) { return row * 9 + column; }
        public static bool NeedFlip(byte[] board, int movefrom, int moveto)
        {
            for (int row = 0; row < 10; ++row)
            {
                for (int column = 0; column < 4; ++column)
                {
                    if (board[row * 9 + column] < board[row * 9 + 8 - column])
                        return true;
                    else if (board[row * 9 + column] > board[row * 9 + 8 - column])
                        return false;
                }
            }
            if (movefrom % 9 != moveto % 9) return movefrom % 9 < moveto % 9;//如果不同列，优先走索引大的
            else return 3 >= movefrom % 9;//如果同列，优先走右边
        }
        public static bool NeedFlip(byte[] board)
        {
            for (int row = 0; row < 10; ++row)
            {
                for (int column = 0; column < 4; ++column)
                {
                    if (board[row * 9 + column] < board[row * 9 + 8 - column])
                        return true;
                    else if (board[row * 9 + column] > board[row * 9 + 8 - column])
                        return false;
                }
            }
            return false;
        }
        public static bool IsRed(byte chess)
        {
            return chess <= 127;
        }
        public static bool IsRedSide(byte[] board)
        {
            for (int k = 3; k < 24; ++k)
                if (board[k] == 3) return false;
            return true;
        }
        public static bool NormalBoard(byte[] board, ref int movefrom, ref int moveto)
        {
            if (0 == board[movefrom]) return false;
            bool redmove = IsRed(board[movefrom]);
            bool redplayer = IsRedSide(board);
            if (redmove != redplayer)
            {
                RotateBoard(board);
                movefrom = RotateIndex(movefrom);
                moveto = RotateIndex(moveto);
            }
            if (NeedFlip(board, movefrom, moveto))
            {
                FlipBoard(board);
                movefrom = FlipIndex(movefrom);
                moveto = FlipIndex(moveto);
            }
            return true;
        }
        public static byte StepForward(byte[] board, int movefrom, int moveto)
        {
            var ate = board[moveto];
            board[moveto] = board[movefrom];
            board[movefrom] = 0;
            return ate;
        }
        public static void StepBackword(byte[] board, int movefrom, int moveto, byte ate)
        {
            board[movefrom] = board[moveto];
            board[moveto] = ate;
        }
        public static bool IsSameSide(byte chess1, byte chess2)
        {
            return IsRed(chess1) == IsRed(chess2);
        }

        public static bool CanMove(byte[] board, int index0, int index1)
        {
            IndexToPosition(index0, out int column0, out int row0);
            IndexToPosition(index1, out int column1, out int row1);
            return CanMove(board, column0, row0, column1, row1);
        }

        public static bool CanMove(byte[] board, int column0, int row0, int column1, int row1)
        {
            var index0 = PositionToIndex(column0, row0);
            var index1 = PositionToIndex(column1, row1);
            var chess = board[index0];
            if (0 != board[index1] && IsSameSide(chess, board[index1])) return false;
            if (127 < chess) chess = (byte)(256 - chess);
            switch (chess)
            {
                case 1: return checkWorker(board, column0, row0, column1, row1);
                case 2: return checkHorse(board, column0, row0, column1, row1);
                case 3: return checkKing(board, column0, row0, column1, row1);
                case 4: return checkSoldier(board, column0, row0, column1, row1);
                case 5: return checkElephant(board, column0, row0, column1, row1);
                case 6: return checkCar(board, column0, row0, column1, row1);
                case 7: return checkCannon(board, column0, row0, column1, row1);
            }
            return true;
        }

        private static bool checkCannon(byte[] board, int column0, int row0, int column1, int row1)
        {
            int sx, sy, ex, ey;
            int counter = board[PositionToIndex(column1, row1)] != 0 ? 1 : 0;
            sx = Math.Min(column0, column1);
            sy = Math.Min(row0, row1);
            ex = Math.Max(column0, column1);
            ey = Math.Max(row0, row1);

            if (column0 == column1)
            {
                int cn = 0;
                for (++sy; sy < ey; ++sy)
                    if (board[sy * 9 + sx] != 0)
                        ++cn;
                return counter == cn;
            }
            if (row0 == row1)
            {
                int cn = 0;
                for (++sx; sx < ex; ++sx)
                    if (board[sy * 9 + sx] != 0)
                        ++cn;
                return counter == cn;
            }
            return false;
        }

        private static bool checkCar(byte[] board, int column0, int row0, int column1, int row1)
        {
            int sx, sy, ex, ey;

            sx = Math.Min(column0, column1);
            sy = Math.Min(row0, row1);
            ex = Math.Max(column0, column1);
            ey = Math.Max(row0, row1);

            if (column0 == column1)
            {
                for (++sy; sy < ey; ++sy)
                    if (board[sy * 9 + sx] != 0)
                        return false;
                return true;
            }
            if (row0 == row1)
            {
                for (++sx; sx < ex; ++sx)
                    if (board[sy * 9 + sx] != 0)
                        return false;
                return true;
            }
            return false;
        }

        private static bool checkElephant(byte[] board, int column0, int row0, int column1, int row1)
        {
            if (Math.Abs(column0 - column1) != 2 || Math.Abs(row0 - row1) != 2) return false;
            if (board[PositionToIndex((column0 + column1) / 2, (row0 + row1) / 2)] != 0) return false;//象眼被卡住
            if ((row0 < 5) != (row1 < 5)) return false;//象不能过河
            return true;
        }

        private static bool checkSoldier(byte[] board, int column0, int row0, int column1, int row1)
        {
            if (Math.Abs(column0 - column1) != 1 || Math.Abs(row0 - row1) != 1) return false;
            if (column1 < 3 || column1 > 5) return false;
            if (row1 > 2 && row1 < 7) return false;
            return true;
        }

        private static bool checkKing(byte[] board, int column0, int row0, int column1, int row1)
        {
            //判断老将对面的情况
            if ((int)board[PositionToIndex(column0, row0)] + board[PositionToIndex(column1, row1)] == 256)
            {
                if (column0 != column1) return false;
                var start = Math.Min(row0, row1);
                var end = Math.Max(row0, row1);
                for (var k = start + 1; k < end; ++k)
                {
                    if (0 != board[PositionToIndex(column0, k)]) return false;
                }
                return true;
            }
            if (Math.Abs(column0 - column1) + Math.Abs(row0 - row1) > 1) return false;//移动距离大于一
            if (column1 < 3 || column1 > 5) return false;//越宫界
            if (row1 > 5) row1 = 9 - row1;
            if (row1 > 2) return false;//越宫界
            return true;
        }

        private static bool checkHorse(byte[] board, int column0, int row0, int column1, int row1)
        {
            if (Math.Abs(column1 - column0) + Math.Abs(row1 - row0) != 3 || 0 == (column1 - column0) * (row1 - row0))
                return false;
            if (Math.Abs(column1 - column0) == 2 && board[column0 + (column1 - column0) / 2 + row0 * 9] != 0)
                return false;
            if (Math.Abs(row1 - row0) == 2 && board[(row0 + (row1 - row0) / 2) * 9 + column0] != 0)
                return false;
            return true;
        }

        private static bool checkWorker(byte[] board, int column0, int row0, int column1, int row1)
        {
            bool redplayer = false;

            for (int k = 0; k < 27; ++k)
                if (256 - 3 == board[k])
                {
                    redplayer = true;
                    break;
                }
            if (IsRed(board[PositionToIndex(column0, row0)]) == redplayer)
            {
                row0 = 9 - row0;
                row1 = 9 - row1;
            }

            if (row1 < row0) return false;//不可逆行
            if (row1 - row0 + Math.Abs(column1 - column0) > 1) return false;//移动距离超过一

            if (row0 < 5 && column0 != column1) return false;//未过河不能横行

            return true;
        }
        public static bool DetectMove(byte[] board1, byte[] board2, out int moveFrom, out int moveTo)
        {
            board1 = board1.Clone() as byte[];
            board2 = board2.Clone() as byte[];
            if (false == IsRedSide(board1)) RotateBoard(board1);
            if (false == IsRedSide(board2)) RotateBoard(board2);
            moveFrom = -1;
            moveTo = -1;
            for (int k = 0; k < 90; ++k)
            {
                if (board1[k] != 0 && board2[k] == 0)
                {
                    if (-1 != moveFrom)
                        return false;
                    else
                        moveFrom = k;
                }
                else if (board1[k] != board2[k])
                {
                    if (-1 != moveTo)
                        return false;
                    else
                        moveTo = k;
                }
            }
            if (-1 == moveFrom || -1 == moveTo) return false;
            return board1[moveFrom] == board2[moveTo];
        }
        public static bool Equares(byte[] board1, byte[] board2)
        {
            if (IsRedSide(board1) != IsRedSide(board2))
            {
                board2 = board2.Clone() as byte[];
                RotateBoard(board2);
            }
            for (int k = 0; k < 90; ++k)
                if (board1[k] != board2[k])
                    return false;
            return true;
        }
        public static string GetTypeName(byte chess)
        {
            switch (chess)
            {
                case 256 - 6: return "車";
                case 256 - 2: return "馬";
                case 256 - 5: return "象";
                case 256 - 4: return "士";
                case 256 - 3: return "将";
                case 256 - 7: return "炮";
                case 256 - 1: return "卒";
                case 6: return "车";
                case 2: return "马";
                case 5: return "相";
                case 4: return "仕";
                case 3: return "帅";
                case 7: return "炮";
                case 1: return "兵";
                default: return "";
            }
        }
        //board为移动后的布局
        public static string GetMoveText(byte[] board, int movefrom, int moveto)
        {
            var chess = board[movefrom];
            var chessName = GetTypeName(chess);
            var red = IsRed(board[movefrom]);
            var redPosText = new char[] { '一', '二', '三', '四', '五', '六', '七', '八', '九' };
            var blackPosText = new char[] { '１', '２', '３', '４', '５', '６', '７', '８', '９' };

            if (IsRedSide(board) == IsRed(chess))//转换成下棋方在上面，索引比较直观
            {
                board = board.Clone() as byte[];
                RotateBoard(board);
                movefrom = RotateIndex(movefrom);
                moveto = RotateIndex(moveto);
            }
            bool scp = false;//是否有重叠
            int row2 = 0;
            string text;
            int column0, row0, column1, row1;
            IndexToPosition(movefrom, out column0, out row0);
            IndexToPosition(moveto, out column1, out row1);

            for (int k = 0; k < 10; ++k)
                if (k != row0 && board[k * 9 + column0] == chess)
                {
                    scp = true;
                    row2 = k;
                }

            if (scp)
                text = (row2 > row0 ? "后" : "前") + chessName;
            else
                text = chessName + (IsRed(chess) ? redPosText[column0] : blackPosText[column0]);

            if (row0 == row1)
            {
                text += "平" + (IsRed(chess) ? redPosText[column1] : blackPosText[column1]);
            }
            else
            {
                if (row1 > row0) text += "进";
                else text += "退";
                int actionIndex;
                if (column0 == column1)
                    actionIndex = Math.Abs(row1 - row0) - 1;
                else
                    actionIndex = column1;
                text += IsRed(chess) ? redPosText[actionIndex] : blackPosText[actionIndex];
            }
            return text;
        }

        internal static string GetMovedText(byte[] board, int moveFrom, int moveTo)
        {
            board = board.Clone() as byte[];
            board[moveFrom] = board[moveTo];
            board[moveTo] = 0;
            return GetMoveText(board, moveFrom, moveTo);
        }
    }

}
