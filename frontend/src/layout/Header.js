import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWarehouse } from "@fortawesome/free-solid-svg-icons";
import "./Header.css";
import { Link } from "react-router-dom";
import LoginForm from "./LoginForm";
import { connect } from "react-redux";


const mapStateToProps = state => {
  return {
    fetching: state.loginReducer.fetching,
    error: state.loginReducer.error,
    accessToken: state.loginReducer.accessToken,
    refreshToken: state.loginReducer.refreshToken,
  };
};

const mapDispatchToProps = dispatch => {
  return {
    login: (payload) => {
      return dispatch({ type: "LOGIN_REQUEST", payload });
    },
  };
};

class Header extends React.Component {
  logout = (event) => {
    window.localStorage.removeItem('accessToken');
    window.localStorage.removeItem('refreshToken');
  }
  render() {
    return (
      <div>
      { !this.props.accessToken || this.props.error ? <LoginForm login={this.props.login.bind(this)}/> : null }
      <nav className="navbar navbar-dark fixed-top bg-dark flex-md-nowrap p-0 shadow bg-image">
        <Link to="/" className="navbar-brand col-sm-3 col-md-2 mr-0">
          Cuply
          <FontAwesomeIcon icon={faWarehouse} className="ml-3" />
        </Link>
        <ul className="navbar-nav px-3">
          <li className="nav-item text-nowrap">
            <a className="nav-link" href="/" onClick={this.logout}>Sign out</a>
          </li>
        </ul>
      </nav>
      </div>
    );
  }
}
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Header);
