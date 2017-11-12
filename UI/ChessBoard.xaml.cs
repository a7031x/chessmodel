using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace UI
{
    /// <summary>
    /// Interaction logic for ChessBoard.xaml
    /// </summary>
    public partial class ChessBoard : UserControl
    {
        private ChessBoardData data = new ChessBoardData();
        private ChessBoardSnap snap;

        public ChessBoard()
        {
            InitializeComponent();
            Reset(true);
        }

        public void Reset(bool redPlayer)
        {
            data.Reset();
            snap = data.GetSnap(0, redPlayer);
            refresh();
        }

        private void refresh()
        {
            int selection = moveList.SelectedIndex;

            refreshList();

            if (-1 == selection)
                moveList.SelectedIndex = 0;
            else
            {
                moveList.SelectedIndex = selection;
            }
        }

        private void refreshList()
        {

            moveList.Items.Clear();
            moveList.Items.Add("开始");
            data.GetMoveList((byte[] board, int moveFrom, int moveTo) =>
            {
                var textBlock = new TextBlock();
                textBlock.Text = moveList.Items.Count.ToString("D3") + ". " + Utility.GetMoveText(board, moveFrom, moveTo);
                var red = Utility.IsRed(board[moveFrom]);
                textBlock.Foreground = new SolidColorBrush(Color.FromScRgb(1, red ? 1 : 0, 0, 0));
                moveList.Items.Add(textBlock);
            });
      //      moveList.Items.Add("跟进");
        }

        private void refreshBoard()
        {
            var list = new List<UIElement>();
            foreach (var child in chessBoard.Children)
            {
                if (child as ChessItem != null)
                    list.Add(child as UIElement);
            }
            foreach (var child in list)
                chessBoard.Children.Remove(child);

            for (int row = 0; row < 10; ++row)
                for (int column = 0; column < 9; ++column)
                {
                    var chess = snap.Board[row * 9 + column];
                    if (0 == chess) continue;
                    var shape = new ChessItem();
                    shape.Type = chess;
                    shape.Column = column;
                    shape.Row = row;
                    shape.Margin = new Thickness(column * 40 - 18, row * 40 - 18, 0, 0);
                    shape.Width = 36;
                    shape.Height = 36;
                    shape.CanCheck = Utility.IsRed(shape.Type) == snap.RedTurn;
                    shape.ChessCheckedHandlers += OnChessChecked;
                    chessBoard.Children.Add(shape);
                }
        }

        //board是移动后的棋盘
        public void SetBoard(byte[] board, bool redPlayer, bool redTurn)
        {
            data.AutoSetBoard(board, redTurn);
         //   if (false == autoTrack) return;
            snap = data.GetCurrentSnap(redPlayer);
            refresh();
        }

        private MoveInformation makeMoveInformation(string description = null)
        {
            var info = new MoveInformation();
            info.Board = snap.Board.Clone() as byte[];
            Utility.StepBackword(info.Board, snap.LastMoveFrom, snap.LastMoveTo, snap.AteType);
            info.MoveFrom = snap.LastMoveFrom;
            info.MoveTo = snap.LastMoveTo;
            info.Description = description;
            return info;
        }
        //棋子选中或取消选中的响应事件
        private void OnChessChecked(object sender, EventArgs e)
        {
            var s = sender as ChessItem;
            foreach (var child in chessBoard.Children)
            {
                if (s.label.IsChecked.Value)//对于取消选中事件，不需要循环关掉其它棋的选中状态
                {
                    var chess = child as ChessItem;
                    if (null != chess)
                    {
                        if (chess != sender)
                            chess.label.IsChecked = false;
                    }
                }
            }
        }
        //分析鼠标对应的棋子位置
        private void parsePosition(Point position, out int column, out int row)
        {
            column = (int)Math.Round(position.X / 40);
            row = (int)Math.Round(position.Y / 40);
        }

        private bool tryPlace(Point position)
        {
            int column;
            int row;
            //判断鼠标是否在合适区域
            parsePosition(position, out column, out row);
            if (column < 0 || row < 0 || column >= 9 || row >= 10) return false;
            var dx = position.X / 40 - column;
            var dy = position.Y / 40 - row;
            if (dx * dx + dy * dy >= 0.16) return false;
            return tryPlace(column, row);
        }

        private ChessItem getSelectedChess()
        {
            foreach (var child in chessBoard.Children)
            {
                var c = child as ChessItem;
                if (null == c) continue;
                if (c.label.IsChecked.Value)
                {
                    return c;
                }
            }
            return null;
        }
        private bool tryPlace(int column, int row)
        {
            //判断是否有棋子已压下
            ChessItem chess = getSelectedChess();
            if (null == chess) return false;

            return Utility.CanMove(snap.Board, chess.Column, chess.Row, column, row);
        }

        private void chessBoard_MouseMove(object sender, MouseEventArgs e)
        {
            //判断该位置是否允许放棋子
            var position = e.GetPosition(chessBoard);
            if (false == tryPlace(position))
            {
                movePreviewer.Visibility = Visibility.Collapsed;
            }
            else
            {
                int column;
                int row;
                parsePosition(position, out column, out row);
                movePreviewer.Margin = new Thickness(column * 40 - 20, row * 40 - 20, 0, 0);
                movePreviewer.Visibility = Visibility.Visible;
            }
        }

        private void chessBoard_MouseRightButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (0 != snap.StepCounter)
            {
                moveList.SelectedIndex = snap.StepCounter - 1;
            }
        }

        private void chessBoard_PreviewMouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            //判断该位置是否允许放棋子
            var position = e.GetPosition(chessBoard);
            int column;
            int row;
            parsePosition(position, out column, out row);

            if (false == tryPlace(position)) return;
            var chess = getSelectedChess();
            data.MoveTo(snap.StepCounter);
            data.Move(snap.RedPlayer, Utility.PositionToIndex(chess.Column, chess.Row), Utility.PositionToIndex(column, row));
            snap = data.GetCurrentSnap(snap.RedPlayer);
            refreshList();
            e.Handled = true;
            moveList.SelectedIndex = moveList.Items.Count - 1;
            snap.StepCounter = moveList.Items.Count - 1;
            ValidateMoves();
        }

        private void refreshScore()
        {
            var move = Python.Instance.Evaluate(snap.Board, snap.RedTurn);
            scoreLabel.Text = $"move: {Utility.GetMoveText(snap.Board, move.Item1, move.Item2)}";
        }

        private void ValidateMoves()
        {
            var board = data.GetCurrentSnap(snap.RedPlayer).Board;
            var moves = Python.Instance.GetMoves(board, data.RedTurn);
            foreach(var move in moves)
            {
                if (Utility.CanMove(board, move.Item1, move.Item2) == false)
                    throw new InvalidOperationException();
            }
            for(int index0 = 0; index0 < 90; ++index0)
            {
                if (Utility.IsRed(board[index0]) != data.RedTurn || board[index0] == 0)
                    continue;
                for(int index1 = 0; index1 < 90; ++index1)
                {
                    if (index0 == index1)
                        continue;
                    if(Utility.CanMove(board, index0, index1))
                    {
                        var move = Tuple.Create(index0, index1);
                        if (moves.Contains(move) == false)
                            throw new InvalidOperationException();
                    }
                }
            }
        }

        private void moveList_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (-1 == moveList.SelectedIndex)
                return;

            snap = data.GetSnap(moveList.SelectedIndex, snap.RedPlayer);

            refreshBoard();
            if (null != moveList.SelectedItem)
                moveList.ScrollIntoView(moveList.SelectedItem);
            refreshScore();
        }

        private void rotateBoard_Click(object sender, RoutedEventArgs e)
        {
            snap = data.GetSnap(snap.StepCounter, !snap.RedPlayer);
            refresh();
        }
    }

    public class MoveInformation : RoutedEventArgs
    {
        public byte[] Board;//移动之前的布局
        public int MoveFrom;
        public int MoveTo;
        public string Description;
    }
}

