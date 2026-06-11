/***********************************************************************
 * Package:     abb_io_controller
 * File:        main.cpp
 * Description: Entry point for abb_io_controller_node.
 * Robot:       ABB IRB6700 175/3.05 on IRBT6004 7m rail
 * Author:      Farzaneh Eskandari
 * Email:       farzane.eskandarii@gmail.com
 * Date:        2026-06-10
 ***********************************************************************/

#include <rclcpp/rclcpp.hpp>
#include "abb_io_controller/io_controller_node.hpp"

static const std::string RWS_IP   = "192.168.0.20";
static const unsigned short RWS_PORT = 80;
static const std::string RWS_USER = "Default User";
static const std::string RWS_PASS = "robotics";

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);

  auto rws_manager = std::make_shared<abb::robot::RWSManager>(
    RWS_IP, RWS_PORT, RWS_USER, RWS_PASS);

  auto node = std::make_shared<abb_io_controller::IOControllerNode>(rws_manager);

  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}