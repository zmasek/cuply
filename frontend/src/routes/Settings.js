import React from "react";
import { connect } from "react-redux";

const mapStateToProps = state => {
  return {
    fetching: state.profileReducer.fetching,
    remoteToken: state.profileReducer.remoteToken,
    id: state.profileReducer.id,
    error: state.profileReducer.error,
    accessToken: state.loginReducer.accessToken,
  };
};

const mapDispatchToProps = dispatch => {
  return {
    loadProfile: () => {
      return dispatch({ type: "PROFILE_READ_REQUEST" });
    },
    saveProfile: (payload) => {
      return dispatch({ type: "PROFILE_UPDATE_REQUEST", payload });
    },
    changeToken: (remoteToken) => {
      return dispatch({ type: "TOKEN_UPDATE", remoteToken })
    }
  };
};

class Settings extends React.Component {
  componentDidMount(){
    if (this.props.id === null) {
      this.props.loadProfile();
    }
    document.title = 'Settings | Cuply';
  }
  componentDidUpdate(prevProps) {
    if (prevProps.accessToken !== this.props.accessToken) {
      this.props.loadProfile();
    }
  }
  saveToken = (e) => {
    e.preventDefault();
    let payload = {id: this.props.id, remoteToken: this.props.remoteToken};
    this.props.saveProfile(payload);
  }
  editToken = (e) => {
    this.props.changeToken(e.target.value);
  }
  setToken(){
    if (this.props.fetching) {
      return "Enter Remote Token";
    } else {
      return this.props.remoteToken;
    }
  }
  render() {
    return (
      <div>
        <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
          <h1 className="h2">Settings</h1>
        </div>
        <form className="form-inline">
          <div className="form-group mb-2">
            <label htmlFor="remoteToken" className="col-sm-2 col-form-label">Remote token</label>
            <input type="text" onChange={this.editToken} className="form-control" id="remoteToken" aria-describedby="remoteTokenHelp" placeholder='Enter token' defaultValue={this.setToken()} />
            <small id="remoteTokenHelp" className="form-text text-muted ml-3">Get the token from the remote service.</small>
          </div>
          <button type="submit" onClick={this.saveToken} className="btn btn-primary mb-2">Save</button>
        </form>
      </div>
    );
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Settings);
