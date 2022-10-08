import React from "react";
import { NavLink } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faEye,
  faTools,
  faSeedling,
  faChartLine,
  faCogs
} from "@fortawesome/free-solid-svg-icons";

function Sidebar() {
  return (
    <nav className="col-sm-2 d-none d-md-block bg-light sidebar">
      <div className="sidebar-sticky">
        <ul className="nav flex-column">
          <li className="nav-item">
            <NavLink
              strict
              exact
              className="nav-link"
              activeClassName="active"
              to="/"
            >
              <FontAwesomeIcon icon={faEye} className="mr-1" />
              Sensors
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink
              strict
              exact
              className="nav-link"
              activeClassName="active"
              to="/actuators/"
            >
              <FontAwesomeIcon icon={faTools} className="mr-1" />
              Actuators
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink
              strict
              exact
              className="nav-link"
              activeClassName="active"
              to="/plants/"
            >
              <FontAwesomeIcon icon={faSeedling} className="mr-1" />
              Plants
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink
              strict
              exact
              className="nav-link"
              activeClassName="active"
              to="/trends/"
            >
              <FontAwesomeIcon icon={faChartLine} className="mr-1" />
              Trends
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink
              strict
              exact
              className="nav-link"
              activeClassName="active"
              to="/settings/"
            >
              <FontAwesomeIcon icon={faCogs} className="mr-1" />
              Settings
            </NavLink>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Sidebar;
