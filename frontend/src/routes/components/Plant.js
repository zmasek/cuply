import React from "react";
import "./Plant.css";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

let options = {
    weekday: "long",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
};

export default class Plant extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      display: true
    }
  }
  deletePlant = (event) => {
    this.setState({display: false});
    // let payload = {id: this.props.id};
    if (!toast.isActive(this.props.id)) {
      toast(`${this.props.name} deleted! Undo?`, {
        position: "bottom-center",
        closeOnClick: true,
        draggable: false,
        toastId: this.props.id,
      });
    }
    //this.props.deletePlant(payload);
  }
  render() {
    let timestamp = new Date(this.props.timestamp).toLocaleString(undefined, options);
    let status = "";
    switch (this.props.status) {
      case 0:
        status = "Germination, sprouting, bud development";
        break;
      case 1:
        status = "Leaf development";
        break;
      case 2:
        status = "Formation of side shoots, tillering";
        break;
      case 3:
        status = "Stem elongation or rosette growth, shoot development";
        break;
      case 4:
        status = "Development of harvestable vegetative plant parts, bolting";
        break;
      case 5:
        status = "Inflorescence emergence, heading";
        break;
      case 6:
        status = "Flowering";
        break;
      case 7:
        status = "Development of fruit";
        break;
      case 8:
        status = "Ripening or maturity of fruit and seed";
        break;
      case 9:
        status = "Senescence, beginning of dormancy";
        break;
      default:
        status = "Unknown";
    };
    return (
      <>
        <div className="card card-width mb-3" style={!this.state.display ? {display: "none"} : {}}>
          <div className="card-img-top card-img-style" style={{backgroundImage: `url(${this.props.image})`}}></div>
          <div className="card-body">
            <h5 className="card-title">{this.props.name}</h5>
            <h6 className="card-subtitle mb-2 text-muted">
              Installed: {timestamp}
            </h6>
            <p className="card-text">
              Status: {status}
            </p>
          </div>
          <div className="card-footer">
            <button className="btn btn-danger float-sm-right" onClick={this.deletePlant}>Delete</button>
          </div>
        </div>
        <ToastContainer closeOnClick={false} />
      </>
    );
  }
}
