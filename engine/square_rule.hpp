#pragma once
#include <array>
#include <vector>
#include <string>

class square_rule_t
{
public:
	struct chess_state_t
	{
		char chess;
		int state;
	};
public:
	std::array<std::vector<chess_state_t>, 90> square_map(const std::string& board)
	{

	}
};