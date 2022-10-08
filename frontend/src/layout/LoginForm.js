import React from "react";
import "./LoginForm.css";


export default class LoginForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: false,
      username: "",
      password: "",
    };
  }

  onChange = (event) => {
    this.setState({
      [event.target.id]: event.target.value
    });
  };

  login = (event) => {
    event.preventDefault();
    let payload = {username: this.state.username, password: this.state.password};
    this.props.login(payload);
  }

  render() {
    return (
      <div className="custom-modal">
        <div className="obfuscator"></div>
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Sign in</h5>
            </div>
            <form onSubmit={this.login}>
              <div className="modal-body">
                <div className="form-group">
                  <label htmlFor="username" className="col-form-label">Username:</label>
                  <input type="text" className="form-control" id="username" onChange={this.onChange} value={this.state.username} />
                </div>
                <div className="form-group">
                  <label htmlFor="password" className="col-form-label">Password:</label>
                  <input type="password" className="form-control" id="password" onChange={this.onChange} value={this.state.password} placeholder="Password" />
                </div>
              </div>
              <div className="modal-footer">
                <button type="submit" className="btn btn-primary" disabled={this.state.username && this.state.password ? "" : true} onClick={this.login}>Login</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }
}
