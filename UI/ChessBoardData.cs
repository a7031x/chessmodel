using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UI
{
    internal class ChessBoardData
    {
        private byte[] board;//当前棋盘
        private bool redTurn = true;
        private List<Step> stepStack = new List<Step>();
        public bool RedTurn { get { return redTurn; } }

        internal ChessBoardData()
        {
            Reset();
        }
        internal void Reset()
        {
            board = new byte[]
            {
                256-6, 256-2, 256-5, 256-4, 256-3, 256-4, 256-5, 256-2, 256-6,
                -0, -0, -0, -0, -0, -0, -0, -0, -0,
                -0, 256-7, -0, -0, -0, -0, -0, 256-7, -0,
                256-1, -0, 256-1, -0, 256-1, -0, 256-1, -0, 256-1,
                -0, -0, -0, -0, -0, -0, -0, -0, -0,
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                1, 0, 1, 0, 1, 0, 1, 0, 1,
                0, 7, 0, 0, 0, 0, 0, 7, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                6, 2, 5, 4, 3, 4, 5, 2, 6
            };
            stepStack.Clear();
            redTurn = true;
        }
        internal void Move(bool redPlayer, int moveFrom, int moveTo)
        {
            if (false == redPlayer)
            {
                moveFrom = Utility.RotateIndex(moveFrom);
                moveTo = Utility.RotateIndex(moveTo);
            }
            var step = Step.Create(board, moveFrom, moveTo);
            stepStack.Add(step);
            step.Forwared(board);
            redTurn = !redTurn;
        }
        internal bool MoveBack()
        {
            if (0 == stepStack.Count) return false;
            var step = stepStack.Last();
            stepStack.Remove(step);
            step.Rollback(board);
            redTurn = !redTurn;
            return true;
        }
        //redTurn 表示
        internal void SetBoard(byte[] board, bool redMoved)
        {
            this.board = board.Clone() as byte[];
            if (false == Utility.IsRedSide(this.board))
                Utility.RotateBoard(this.board);
            this.redTurn = !redMoved;
            stepStack.Clear();
        }
        internal void AutoSetBoard(byte[] board, bool redMoved)
        {
            int moveFrom, moveTo;
            if (redMoved != redTurn || false == Utility.DetectMove(this.board, board, out moveFrom, out moveTo) || Utility.IsRed(this.board[moveFrom]) != redTurn)
            {
                if (0 == stepStack.Count)
                    SetBoard(board, redMoved);
                else
                {
                    MoveBack();
                    AutoSetBoard(board, redMoved);
                }
            }
            else
                Move(true, moveFrom, moveTo);
        }

        internal ChessBoardSnap GetSnap(int stepCounter, bool redPlayer)
        {
            if (stepCounter > stepStack.Count || 0 > stepCounter) return null;
            var snap = new ChessBoardSnap();
            snap.Board = board.Clone() as byte[];
            snap.StepCounter = stepStack.Count;
            snap.RedTurn = redTurn;
            if (stepCounter != 0)
            {
                var step = stepStack.ElementAt(stepCounter - 1);
                snap.LastMoveFrom = step.MoveFrom;
                snap.LastMoveTo = step.MoveTo;
                snap.AteType = step.EatType;
            }
            else
            {
                snap.LastMoveFrom = 0;
                snap.LastMoveTo = 0;
                snap.AteType = 0;
            }

            while (snap.StepCounter > stepCounter)
            {
                var step = stepStack.ElementAt(--snap.StepCounter);
                step.Rollback(snap.Board);
                snap.RedTurn = !snap.RedTurn;
            }
            if (false == redPlayer)
            {
                Utility.RotateBoard(snap.Board);
                snap.LastMoveFrom = Utility.RotateIndex(snap.LastMoveFrom);
                snap.LastMoveTo = Utility.RotateIndex(snap.LastMoveTo);
            }
            return snap;
        }

        internal ChessBoardSnap GetCurrentSnap(bool redPlayer)
        {
            return GetSnap(stepStack.Count, redPlayer);
        }

        internal void MoveTo(int stepIndex)
        {
            while (stepStack.Count > stepIndex)
                MoveBack();
        }
        internal void GetMoveList(Action<byte[], int, int> callback)
        {
            var snap = GetSnap(0, true);
            foreach (var step in stepStack)
            {
                callback(snap.Board, step.MoveFrom, step.MoveTo);
                step.Forwared(snap.Board);
            }
        }
    }
    internal class ChessBoardSnap
    {
        internal byte[] Board;//获取StepCounter时刻的棋盘快照
        internal int StepCounter;//0表示未移动过，最大为当前所有步数
        internal bool RedTurn;//当前是否红走
        internal int LastMoveFrom;//上一次移动源
        internal int LastMoveTo;//上一次移动目标
        internal byte AteType;//被吃掉的棋
        internal bool RedPlayer { get { return Utility.IsRedSide(Board); } }
    }
    class Step
    {
        internal byte Type;
        internal byte EatType;
        internal int MoveFrom;
        internal int MoveTo;
        internal static Step Create(byte[] board, int moveFrom, int moveTo)
        {
            var state = new Step();
            state.Type = board[moveFrom];
            state.EatType = board[moveTo];

            state.MoveFrom = moveFrom;
            state.MoveTo = moveTo;
            return state;
        }

        internal void Rollback(byte[] board)
        {
            board[MoveFrom] = board[MoveTo];
            board[MoveTo] = this.EatType;
        }

        internal void Forwared(byte[] board)
        {
            board[MoveTo] = board[MoveFrom];
            board[MoveFrom] = 0;
        }
    }
}
