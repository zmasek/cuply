import React from "react";
import { connect } from "react-redux";
import Graph from "./components/Graph";


const mapStateToProps = state => {
  return {
    fetching: state.sensorsReducer.fetching,
    sensors: state.sensorsReducer.sensors,
    error: state.sensorsReducer.error,
    accessToken: state.loginReducer.accessToken,
  };
};
const mapDispatchToProps = dispatch => {
  return {
    readSensors: (payload) => {
      return dispatch({ type: "SENSOR_READ_REQUEST", payload });
    },
    createSensor: (payload) => {
      return dispatch({ type: "SENSOR_CREATE_REQUEST", payload });
    },
    deleteSensor: (payload) => {
      return dispatch({ type: "SENSOR_DELETE_REQUEST", payload });
    },
  };
};

class Trends extends React.Component {
  constructor() {
    super();

    this.state = {
      currentDate: new Date(),
      next: false
    };
  }
  componentDidMount(){
    if (this.props.sensors.length === 0) {
      let payload = {"fsm_class!": "DigitalActuator"};
      this.props.readSensors(payload);
    }
    document.title = 'Trends | Cuply';
  }
  componentDidUpdate(prevProps){
    if (prevProps.accessToken !== this.props.accessToken) {
      let payload = {"fsm_class!": "DigitalActuator"};
      this.props.readSensors(payload);
    }
  }
  createTrends() {
    const canProceed = this.props.sensors.length !== 0;
    if (canProceed) {
      let graphs = [];
      for (const sensor of this.props.sensors) {
        graphs.push(<Graph device={sensor} key={sensor["id"]} date={this.state.currentDate} />);
      }
      return graphs;
    }
  }
  getCurrentDate(){
    const currentDate = this.state.currentDate;
    const year = currentDate.getFullYear();
    const month = (currentDate.getMonth() + 1).toString();
    const normalizedMonth = `${month.length === 1 ? "0" : ""}${month}`;
    const day = currentDate.getDate().toString();
    const normalizedDay = `${day.length === 1 ? "0" : ""}${day}`;
    return `${normalizedDay}.${normalizedMonth}.${year}.`
  }
  navigate(direction){
    const options = { year: 'numeric', month: 'numeric', day: 'numeric' };
    let newDate = new Date(this.state.currentDate.getTime());
    if (direction === 'next') {
      newDate.setDate(this.state.currentDate.getDate() + 1);
    } else if (direction === 'previous') {
      newDate.setDate(this.state.currentDate.getDate() - 1);
    }
    this.setState({
      next: newDate.toLocaleDateString(undefined, options) !== new Date().toLocaleDateString(undefined, options),
      currentDate: newDate
    });
  }
  render() {
    return (
      <div>
        <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
          <h1 className="h2">Trends</h1>
        </div>
        <nav aria-label="Page navigation example">
          <ul className="pagination justify-content-center">
            <li className="page-item">
              <button className="page-link" aria-label="Previous" onClick={() => this.navigate('previous')}>
                <span aria-hidden="true">&laquo;</span>
              </button>
            </li>
            <li className="page-item disabled"><button className="page-link">{this.getCurrentDate()}</button></li>
            <li className={`${"page-item "}${this.state.next ? '' : 'disabled'}`}>
              <button className="page-link" aria-label="Next" onClick={() => this.navigate('next')}>
                <span aria-hidden="true">&raquo;</span>
              </button>
            </li>
          </ul>
        </nav>
        <div>
          {this.createTrends()}
        </div>
      </div>
    );
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Trends);
