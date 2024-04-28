import React from "react";

class CloseIcon extends React.Component<{
  className?: string;
  stroke: string;
}> {
  override render() {
    const { className = undefined, stroke } = this.props;
    return (
      <svg className={className} width="30" height="30" viewBox="0 0 30 30">
        <path
          d="M22.5 7.5L7.5 22.5"
          stroke={stroke || "#FFFFFF"}
          strokeLinecap="square"
          strokeLinejoin="round"
        />
        <path
          d="M7.5 7.5L22.5 22.5"
          stroke={stroke || "#FFFFFF"}
          strokeLinecap="square"
          strokeLinejoin="round"
        />
      </svg>
    );
  }
}

export default CloseIcon;
