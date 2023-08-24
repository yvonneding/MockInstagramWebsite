import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Posts from './posts';

class Feed extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      list: [],
      next: '',
    };
    this.fetchdata = this.fetchdata.bind(this);
    if (window.PerformanceNavigation.type === 2) {
      this.state = window.history.state;
    }
  }

  componentDidMount() {
    const { url } = this.props;
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          list: data.results,
          next: data.next,
        });
      })
      .catch((error) => console.log(error));
  }

  fetchdata() {
    const { next } = this.state;
    fetch(next, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState((prevState) => ({
          list: prevState.list.concat(data.results),
          next: data.next,
        }));
      })
      .catch((error) => console.log(error));
  }

  render() {
    const { list } = this.state;
    const { next } = this.state;
    return (
      <InfiniteScroll
        dataLength={list.length}
        next={this.fetchdata}
        hasMore={next !== ''}
      >
        <div>
          {list.map((result) => (
            <div key={result.postid}>
              <Posts
                url={result.url}
                postid={result.postid}
              />
            </div>
          ))}
        </div>
      </InfiniteScroll>
    );
  }
}

Feed.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Feed;
