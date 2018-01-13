#pragma once
#include <vector>
#include <string>
#include <memory>

class model_t abstract
{
public:
	virtual std::vector<float> predict(const std::vector<std::string> &boards, bool red) = 0;
	static std::shared_ptr<model_t> create();
};