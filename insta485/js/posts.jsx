import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import Likes from './likes';
import Comments from './comments';

class Posts extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      age: 0,
      imgurl: ' ',
      owner: ' ',
      ownerimgurl: ' ',
      postid: 0,
      numLikes: 0,
      lognamelikesthis: 0,
      buttonname: '',
    };
    this.handlesingleclick = this.handlesingleclick.bind(this);
    this.handledoubleclick = this.handledoubleclick.bind(this);
  }

  componentDidMount() {
    const { url } = this.props;
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const { postid } = this.props;
        this.setState({
          age: data.age,
          imgurl: data.img_url,
          owner: data.owner,
          ownerimgurl: data.owner_img_url,
          postid,
        });
      })
      .catch((error) => console.log(error));
    const likeurl = `${url}likes/`;
    fetch(likeurl, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          numLikes: data.likes_count,
          lognamelikesthis: data.logname_likes_this,
        });
        const { lognamelikesthis } = this.state;
        this.setState({
          buttonname: (lognamelikesthis === 0 ? 'like' : 'unlike'),
        });
      })
      .catch((error) => console.log(error));
  }

  handledoubleclick() {
    const { url } = this.props;
    const { lognamelikesthis } = this.state;
    if (lognamelikesthis === 0) {
      fetch(`${url}likes/`, {
        credentials: 'same-origin',
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then(() => {
          const { numLikes } = this.state;
          this.setState({
            numLikes: numLikes + 1,
            lognamelikesthis: 1,
            buttonname: 'unlike',
          });
        });
    }
  }

  handlesingleclick() {
    const { url } = this.props;
    const { lognamelikesthis } = this.state;
    const { buttonname } = this.state;
    const { numLikes } = this.state;
    this.setState({
      numLikes: (lognamelikesthis === 0 ? (numLikes + 1) : (numLikes - 1)),
      lognamelikesthis: (lognamelikesthis === 0 ? 1 : 0),
      buttonname: (buttonname !== 'unlike' ? 'unlike' : 'like'),
    });
    fetch(`${url}likes/`, {
      method: (lognamelikesthis === 0 ? 'POST' : 'DELETE'),
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
    });
  }

  render() {
    const { url } = this.props;
    const { age } = this.state;
    const { ownerimgurl } = this.state;
    const { owner } = this.state;
    const { imgurl } = this.state;
    const { postid } = this.state;
    const { numLikes } = this.state;
    const { lognamelikesthis } = this.state;
    const { buttonname } = this.state;
    return (
      <div className="posts">
        <p>
          <a href={`/u/${owner}/`}><img src={ownerimgurl} alt="owner_img" width="50" height="60" /></a>
          <a href={`/u/${owner}/`}>{owner}</a>
          {' '}
          <a href={`/p/${postid}/`}>{moment.utc(age).fromNow()}</a>
        </p>
        <p>
          <img
            src={imgurl}
            alt="post_img"
            onDoubleClick={this.handledoubleclick}
          />
        </p>
        <Likes
          url={`${url}likes/`}
          numLikes={numLikes}
          logname_likes_this={lognamelikesthis}
          buttonname={buttonname}
          handlesingleclick={this.handlesingleclick}
        />
        <Comments url={`${url}comments/`} />
      </div>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
  postid: PropTypes.number,
};

Posts.defaultProps = {
  postid: 0,
};
export default Posts;
