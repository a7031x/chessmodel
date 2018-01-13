using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TensorFlow;

namespace csmodel
{
    public class Model
    {
        private TFSession session;
        public Model(string path)
        {
            var graph = new TFGraph();
            var model = File.ReadAllBytes(path);
            graph.Import(model);
            session = new TFSession(graph);
        }
    }
}
