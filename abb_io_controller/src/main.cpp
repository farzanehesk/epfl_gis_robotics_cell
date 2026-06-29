/***********************************************************************
 * Package:     abb_io_controller
 * File:        main.cpp
 * Description: Entry point for abb_io_controller_node.
 *              RWS credentials loaded from ROS2 parameters
 *              (set via config/rws_credentials.yaml — gitignored).
 * Robot:       ABB IRB6700 175/3.05 on IRBT6004 7m rail
 * Author:      Farzaneh Eskandari
 * Email:       farzane.eskandarii@gmail.com
 * Date:        2026-06-10
 ***********************************************************************/

#include <rclcpp/rclcpp.hpp>
#include "abb_io_controller/io_controller_node.hpp"

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);

  // Read RWS credentials from ROS2 parameters
  // Loaded from config/rws_credentials.yaml via launch file
  auto param_node = std::make_shared<rclcpp::Node>("abb_io_controller_params");
  param_node->declare_parameter("rws_ip",   "192.168.0.20");
  param_node->declare_parameter("rws_port", 80);
  param_node->declare_parameter("rws_user", "Default User");
  param_node->declare_parameter("rws_pass", "robotics");

  const std::string  rws_ip   = param_node->get_parameter("rws_ip").as_string();
  const unsigned short rws_port = static_cast<unsigned short>(
                                    param_node->get_parameter("rws_port").as_int());
  const std::string  rws_user = param_node->get_parameter("rws_user").as_string();
  const std::string  rws_pass = param_node->get_parameter("rws_pass").as_string();

  RCLCPP_INFO(rclcpp::get_logger("main"), "Connecting to RWS at %s:%d as '%s'",
              rws_ip.c_str(), rws_port, rws_user.c_str());

  auto rws_manager = std::make_shared<abb::robot::RWSManager>(
    rws_ip, rws_port, rws_user, rws_pass);

  // Initialize RWS session — required before any write calls
  try
  {
    auto description = rws_manager->collectAndParseSystemData("rob1_");
    RCLCPP_INFO(rclcpp::get_logger("main"), "Connected to: %s",
                description.header().system_name().c_str());

    // Initialize priority interface session before any write calls
    rws_manager->runPriorityService(
      [](abb::rws::RWSStateMachineInterface& interface)
      {
        interface.getSystemInfo();
      });
  }
  catch (const std::exception& e)
  {
    RCLCPP_ERROR(rclcpp::get_logger("main"), "Failed to connect to robot: %s", e.what());
    return 1;
  }

  auto node = std::make_shared<abb_io_controller::IOControllerNode>(rws_manager);

  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}