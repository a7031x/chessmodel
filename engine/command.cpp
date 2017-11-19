#include <vector>
#include <string>
#include <sstream>
#include <iterator>
#include <algorithm>
#include "search.hpp"

std::vector<std::string> split(const std::string& text)
{
	std::istringstream iss(text);
	std::vector<std::string> results((std::istream_iterator<std::string>(iss)), std::istream_iterator<std::string>());
	return results;
}

std::string join(const std::vector<std::string>& tokens, const std::string& separator,
	const std::string& left = "", const std::string& right = "")
{
	std::string r = left;
	int index = 0;
	for (auto& token : tokens)
	{
		if (index++)
			r += separator;
		r += token;
	}
	r += right;
	return r;
}

std::string format_moves(const std::vector<std::pair<int, int>>& moves)
{
	std::vector<std::string> parts;
	for (auto move : moves)
	{
		parts.push_back("(" + std::to_string(move.first) + "," + std::to_string(move.second) + ")");
	}
	return join(parts, ",", "[", "]");
}

std::string format_boards(const std::vector<std::string>& boards)
{
	auto parts = boards;
	for (auto& x : parts)
	{
		std::replace(x.begin(), x.end(), ' ', '#');
		x = '\'' + x + '\'';
	}
	return join(parts, ",", "[", "]");
}

std::string format_scores(const std::vector<int>& scores)
{
	std::vector<std::string> parts;
	for (auto score : scores)
		parts.push_back(std::to_string(score));
	return join(parts, ",", "[", "]");
}
//get_moves 1 rhebkbehr##########c#####c#p#p#p#p#p##################P#P#P#P#P#C#####C##########RHEBKBEHR
std::string command(const std::vector<std::string>& tokens)
{
	if ("get_moves" == tokens[0])
	{
		int red = std::stoi(tokens[1]);
		std::string board = tokens[2];
		std::replace(board.begin(), board.end(), '#', ' ');
		auto moves = move_t::next_steps(board, red ? true : false);
		return format_moves(moves);
	}
	else if ("search" == tokens[0])
	{
		int red = std::stoi(tokens[1]);
		std::string board = tokens[2];
		int depth = std::stoi(tokens[3]);
		std::replace(board.begin(), board.end(), '#', ' ');
		static search_t search;
		auto pack = search.search(board, red, depth);
		std::vector<std::pair<int, int>> moves;
		std::vector<std::string> boards;
		std::vector<int> scores;
		for (auto x : pack)
		{
			moves.push_back(x.move);
			boards.push_back(x.board);
			scores.push_back(x.score);
		}
		return join({ format_moves(moves), format_scores(scores), format_boards(boards) }, ",", "(", ")");
	}
	return "";
}

extern "C" {
	char* command(const char* cmd)
	{
		auto tokens = split(cmd);
		auto r = command(tokens);
		auto cr = (char*)malloc(r.length() + 1);
		strcpy_s(cr, r.length() + 1, r.data());
		return cr;
	}
}
