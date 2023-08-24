import React from 'react';
import PropTypes from 'prop-types';

class Likes extends React.Component {
  /* Display number of likes and like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    const { handlesingleclick } = this.props;
    handlesingleclick();
  }

  render() {
    const { numLikes } = this.props;
    const { buttonname } = this.props;
    // Render number of likes
    return (
      <div>
        <p>
          {numLikes}
          {' '}
          like
          {numLikes !== 1 ? 's' : ''}
        </p>
        <button className="like-unlike-button" type="button" onClick={() => this.handleClick()}>{buttonname}</button>
      </div>
    );
  }
}

Likes.propTypes = {
  numLikes: PropTypes.number,
  handlesingleclick: PropTypes.func,
  buttonname: PropTypes.string,
};

Likes.defaultProps = {
  numLikes: 0,
  handlesingleclick: null,
  buttonname: '',
};

export default Likes;
