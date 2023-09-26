import React from "react";

class DownIcon extends React.Component {
  render() {
    const { className, stroke } = this.props;
    return (
      <svg className={className} width="30" height="18" fill="none" viewBox="0 0 30 18">
        <path d="M28.5 1.75L15 15.25L1.5 1.75" stroke={stroke || "black"} strokeWidth="3" />
      </svg>
    );
  }
}

export default DownIcon;
