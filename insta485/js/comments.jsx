import React from 'react';
import PropTypes from 'prop-types';

class Comments extends React.Component {
  constructor(props) {
    super(props);
    this.state = { comments: [], temp: '' };
    this.handlechange = this.handlechange.bind(this);
    this.handlesubmit = this.handlesubmit.bind(this);
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
          comments: data.comments,
        });
      })
      .catch((error) => console.log(error));
  }

  handlechange(event) {
    this.setState({ temp: event.target.value });
  }

  handlesubmit(event) {
    const { url } = this.props;
    const { temp } = this.state;
    fetch(url, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: temp,
      }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const { comments } = this.state;
        const copycomments = comments.slice();
        copycomments.push(data);
        this.setState({ comments: copycomments, temp: '' });
      })
      .catch((error) => console.log(error));
    event.preventDefault();
  }

  render() {
    const { comments } = this.state;
    const { temp } = this.state;
    return (
      <form onSubmit={this.handlesubmit} className="comment-form">
        <div>
          { comments.map((comment) => (
            <div key={comment.commentid}>
              <a href={`/u/${comment.owner}/`}>{comment.owner}</a>
              {comment.text}
            </div>
          )) }
        </div>
        <input type="text" onChange={this.handlechange} value={temp} />
      </form>
    );
  }
}

Comments.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Comments;
