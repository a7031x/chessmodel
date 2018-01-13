#pragma once
#include <vector>
#include <string>
#include <memory>

class model_t
{
public:
	model_t();
	static std::vector<float> predict(const std::vector<std::string> &boards, bool red);

private:
	std::shared_ptr<class ClientSession> _session;
};