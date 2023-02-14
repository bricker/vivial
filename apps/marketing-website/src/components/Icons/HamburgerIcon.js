import React from 'react';

class HamburgerIcon extends React.Component {
  render() {
    const { className, stroke } = this.props;
    return (
      <svg className={className} width="34" height="34" viewBox="0 0 34 34">
        <path d="M7.0835 9.91669H26.9168" stroke={stroke || 'black'} strokeLinecap="round" />
        <path d="M7.0835 17H26.9168" stroke={stroke || 'black'} strokeLinecap="round" />
        <path d="M7.0835 24.0833H26.9168" stroke={stroke || 'black'} strokeLinecap="round" />
      </svg>
    );
  }
}

export default HamburgerIcon;
