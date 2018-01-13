#include "model.h"
#include "square_rule.hpp"
#include <vector>
#include <tensorflow/cc/saved_model/loader.h>
#include <tensorflow/cc/client/client_session.h>
#include <tensorflow/cc/ops/standard_ops.h>
#include <tensorflow/core/framework/tensor.h>

class model_imply : model_t
{
public:
	model_imply()
	{
		_bundle = std::make_shared<tensorflow::SavedModelBundle>();
		auto status = tensorflow::LoadSavedModel(tensorflow::SessionOptions(), tensorflow::RunOptions(), "./model/1.4", { "serve" }, &*_bundle);
		assert(status.ok());
	}

	std::vector<float> predict(const std::vector<std::string> &boards, bool red) override
	{
		std::vector<square_rule_t::square_map_t> maps;
		std::vector<int> scores;
		for (auto& board : boards)
		{
			square_rule_t::square_map_t map;
			int score;
			std::tie(map, score) = normalized_map_and_score(board, red);
			maps.push_back(map);
			scores.push_back(score);
		}

		auto batch_size = (int)boards.size();
		std::vector<std::array<int, 90>> length;
		for (auto& map : maps)
		{
			std::array<int, 90> x;
			for (int k = 0; k < 90; ++k)
				x[k] = map[k].size();
			length.push_back(x);
		}

		tensorflow::Tensor input_length(tensorflow::DT_FLOAT, tensorflow::TensorShape({ batch_size, 90 });
		auto input_map = create_feed_from_map(maps);
		auto input_scores = create_feed_from_score(scores);
	}

private:
	tensorflow::Tensor create_feed_from_map(const std::vector<square_rule_t::square_map_t>& maps)
	{

	}

	std::pair<square_rule_t::square_map_t, int> normalized_map_and_score(const std::string& board, bool red)
	{
		auto board = normalize_board(board, red);
		return std::make_pair(square_rule_t::square_map(board), rule_t::basic_score(board));
	}

	std::string normalize_board(const std::string& board, bool red)
	{
		std::string r;
		if (false == red)
		{
			for (auto piece : board)
				r += rule_t::flip_side(piece);
		}
		else
			r = board;
		if (board.find('K', 0) < 45)
			return rule_t::rotate_board(r);
		else
			return r;
	}

private:
	std::shared_ptr<tensorflow::SavedModelBundle> _bundle;
};

std::shared_ptr<model_t> model_t::create()
{
	return std::static_pointer_cast<model_t, model_imply>(std::make_shared<model_imply>());
}
