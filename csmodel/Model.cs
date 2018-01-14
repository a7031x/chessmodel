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
            var metaGraph = new TFBuffer();
            session = new TFSession();
            var sess = session.FromSavedModel(new TFSessionOptions(), null, path, new[] { "serve" }, graph, metaGraph);
            session = sess;
        }

        public float[] Predict(IEnumerable<string> boards, bool red)
        {
            var batch = boards.Count();
            var (squares, lengths, scores) = Feeder.Feed(boards, red);
            var mlen = lengths.Max();
            var inputLength = TFTensor.FromBuffer(new TFShape(batch, 90), lengths, 0, lengths.Length);
            var inputSquare = TFTensor.FromBuffer(new TFShape(batch, 90, mlen, 2), squares, 0, squares.Length);
            var inputBasicScore = TFTensor.FromBuffer(new TFShape(batch), scores, 0, scores.Length);
            scores = Predict(inputSquare, inputLength, inputBasicScore);
            scores = scores.Select(x => red ? x : -x).ToArray();
            return scores;
        }

        private float[] Predict(TFTensor inputSquare, TFTensor inputLength, TFTensor inputBasicScore)
        {
            var runner = session.GetRunner();
            runner.AddInput("Model/input/input_square", inputSquare);
            runner.AddInput("Model/input/input_length", inputLength);
            runner.AddInput("Model/input/input_basic_score", inputBasicScore);
            runner.AddTarget("Model/score/score");
            var results = runner.Fetch("Model/score/score").Run();
            var scores = results[0].GetValue() as float[];
            return scores;
        }
    }
}
