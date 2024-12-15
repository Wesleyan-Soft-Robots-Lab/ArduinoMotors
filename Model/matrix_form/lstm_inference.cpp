#include <iostream>
#include <fstream>
#include <Eigen/Core>
#include <vector>
#include <tuple>
#include <chrono>

using namespace Eigen;

/*
(3804, 40, 2)
[(64, 2), (64, 16)] (2, 64, 16) (2, 64) (1, 16) (2,)
*/

std::vector<std::string> splitString(const std::string &str, char delimiter)
{
    std::vector<std::string> tokens;
    std::string token;
    std::stringstream ss(str);

    while (std::getline(ss, token, delimiter))
    {
        tokens.push_back(token);
    }

    return tokens;
}

Matrix<double, 64, 2> W_1h;
Matrix<double, 64, 16> W_2h;
std::vector<MatrixXd> W_hh(2, MatrixXd(64, 16));
Matrix<double, 2, 64> b_h;
Matrix<double, 1, 16> W;
Matrix<double, 2, 2> b;
std::vector<MatrixXd> test_array(3804, MatrixXd(40, 2));

void load_test_array()
{
    std::ifstream file("test_array1.txt");
    std::string line;
    for (int i = 0; i < 3804; i++)
    {
        for (int j = 0; j < 40; j++)
        {
            std::getline(file, line);
            std::vector<std::string> tokens = splitString(line, ',');
            for (int k = 0; k < 2; k++)
            {
                test_array[i](j, k) = std::stod(tokens[k]);
            }
        }
    }
    file.close();
}

void load_model_weights()
{
    std::ifstream file("LSTMRegressorWeights_strap_42.txt");
    std::string line;
    for (int i = 0; i < 2; i++)
    {
        for (int j = 0; j < 64; j++)
        {
            std::getline(file, line);
            std::vector<std::string> tokens = splitString(line, ',');
            for (int k = 0; k < 16; k++)
            {
                W_hh[i](j, k) = std::stod(tokens[k]);
            }
        }
    }

    for (int i = 0; i < 2; i++)
    {
        std::getline(file, line);
        std::vector<std::string> tokens = splitString(line, ',');
        for (int j = 0; j < 64; j++)
        {
            b_h(i) = std::stod(tokens[j]);
        }
    }

    std::getline(file, line);
    std::vector<std::string> tokens = splitString(line, ',');
    for (int i = 0; i < 16; i++)
    {
        W(0, i) = std::stod(tokens[i]);
    }

    std::getline(file, line);
    b(0, 0) = std::stod(line);

    for (int i = 0; i < 64; i++)
    {
        std::getline(file, line);
        tokens = splitString(line, ',');
        for (int j = 0; j < 2; j++)
        {
            W_1h(i, j) = std::stod(tokens[j]);
        }
    }

    for (int i = 0; i < 64; i++)
    {
        std::getline(file, line);
        tokens = splitString(line, ',');
        for (int j = 0; j < 16; j++)
        {
            W_2h(i, j) = std::stod(tokens[j]);
        }
    }
}

MatrixXd sigmoid(MatrixXd x)
{
    return 1 / (1 + (-x).array().exp());
}

MatrixXd tanh(MatrixXd x)
{
    return x.array().tanh();
}

std::tuple<MatrixXd, MatrixXd> calc_lstm_cell(MatrixXd x, MatrixXd h, MatrixXd c, MatrixXd W_ih, MatrixXd W_hh, MatrixXd b_h)
{
    MatrixXd gates = x * W_ih.transpose() + h * W_hh.transpose() + b_h;
    MatrixXd i = sigmoid(gates.block(0, 0, 1, 16));
    MatrixXd f = sigmoid(gates.block(0, 16, 1, 16));
    MatrixXd g = tanh(gates.block(0, 32, 1, 16));
    MatrixXd o = sigmoid(gates.block(0, 48, 1, 16));
    c = f.array() * c.array() + i.array() * g.array();
    h = o.array() * c.array().tanh();
    return std::make_tuple(h, c);
}

MatrixXd lstm_forward(Matrix<double, 40, 2> x)
{
    const int hidden_size = 16;
    MatrixXd hidden = MatrixXd::Zero(2, hidden_size);
    MatrixXd cell = MatrixXd::Zero(2, hidden_size);
    int seq_len = x.rows();
    for (int t = 0; t < seq_len; t++)
    {
        auto [new_h0, new_c0] = calc_lstm_cell(x.row(t), hidden.row(0), cell.row(0), W_1h, W_hh[0], b_h.row(0));
        cell.row(0) = new_c0;
        hidden.row(0) = new_h0;

        auto [new_h1, new_c1] = calc_lstm_cell(hidden.row(0), hidden.row(1), cell.row(1), W_2h, W_hh[1], b_h.row(1));
        cell.row(1) = new_c1;
        hidden.row(1) = new_h1;
    }
    return hidden.row(1);
}

MatrixXd fc_forward(Matrix<double, 1, 16> x)
{
    return x * W.transpose() + b;
}

int main()
{
    load_test_array();
    load_model_weights();


    auto start = std::chrono::high_resolution_clock::now();

    Vector<double, 3804> output;
    int counter = 0;
    for (auto& i : test_array)
    {
        output[counter] = fc_forward(lstm_forward(i))(0);
        counter++;
    }

    auto end = std::chrono::high_resolution_clock::now();

    // std::cout << output << std::endl
    //           << std::endl;

    std::cout << "Time taken: " << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() / 1000.0 << "s" << std::endl;

    return 0;
}