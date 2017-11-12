using System;
using System.Collections.Generic;
using System.Linq;

using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Media;

namespace UI
{
    /// <summary>
    /// Interaction logic for Chess.xaml
    /// </summary>
    public partial class ChessItem : UserControl
    {
        public byte Type { set; get; }
        public delegate void OnChessChecked(object sender, EventArgs e);
        public OnChessChecked ChessCheckedHandlers;
        public ChessItem()
        {
            InitializeComponent();
            label.DataContext = this;
            CanCheck = true;
        }

        private void label_Checked(object sender, RoutedEventArgs e)
        {
            ChessCheckedHandlers?.Invoke(this, null);
        }

        public bool CanCheck { get; set; }

        public int Column { get; set; }
        public int Row { get; set; }
    }

    public class ChessToStringConverter : IValueConverter
    {
        #region IValueConverter Members
        public static ChessToStringConverter Value = new ChessToStringConverter();
        public object Convert(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            //var chess = value as byte;
            var chess = (byte)value;
            return Utility.GetTypeName(chess);
        }
        public object ConvertBack(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            throw new NotImplementedException();
        }

        #endregion
    }
    public class ChessToBrushConverter : IValueConverter
    {
        public static ChessToBrushConverter Value = new ChessToBrushConverter();
        #region IValueConverter Members
        public object Convert(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            SolidColorBrush brush = new SolidColorBrush();
            brush.Color = (byte)value > 127 ? Color.FromRgb(0, 0, 0) : Color.FromRgb(180, 0, 0);
            return brush;
        }

        public object ConvertBack(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
        {
            throw new NotImplementedException();
        }

        #endregion
    }
}
