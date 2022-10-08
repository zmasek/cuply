import React from "react";
import { connect } from "react-redux";
import Plant from "./components/Plant";
import PlantForm from "./components/PlantForm";
import "./Plants.css";

const mapStateToProps = state => {
  return {
    fetching: state.plantsReducer.fetching,
    plants: state.plantsReducer.plants,
    remoteId: state.plantsReducer.remoteId,
    error: state.plantsReducer.error,
    accessToken: state.loginReducer.accessToken,
  };
};

const mapDispatchToProps = dispatch => {
  return {
    readPlants: () => {
      return dispatch({ type: "PLANT_READ_REQUEST" });
    },
    createPlant: (payload) => {
      return dispatch({ type: "PLANT_CREATE_REQUEST", payload });
    },
    deletePlant: (payload) => {
      return dispatch({ type: "PLANT_DELETE_REQUEST", payload });
    },
  };
};

class Plants extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      modalState: false,
    }
  }
  componentDidMount() {
    if (this.props.plants.length === 0) {
      this.props.readPlants();
    }
    document.title = 'Plants | Cuply';
  }
  componentDidUpdate(prevProps) {
    if (prevProps.accessToken !== this.props.accessToken) {
      this.props.readPlants();
    }
  }
  createPlants = () => {
    const canProceed = this.props.plants.length !== 0;
    if (canProceed) {
      let cards = [];
      for (const card of this.props.plants) {
        cards.push(
          <Plant
            key={card.id}
            id={card.id}
            timestamp={card.timeInstalled}
            status={card.currentState}
            remoteId={card.remoteId}
            name={card.name}
            image={card.imageUrl}
            deletePlant={this.props.deletePlant.bind(this)}
          />
        );
      }
      return cards;
    }
  }
  toggleModal = (e) => {
    this.setState({modalState: !this.state.modalState});
  }
  render() {
    return (
      <div className="plants">
        { this.state.modalState ? <PlantForm createPlant={this.props.createPlant.bind(this)} toggle={this.toggleModal.bind(this)}/> : null }
        <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
          <h1 className="h2">Plants</h1>
          <button className="btn btn-success" onClick={this.toggleModal}>Add</button>
        </div>
        <div className="card-deck">
          {this.createPlants()}
        </div>
      </div>
    );
  }
}
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Plants);
