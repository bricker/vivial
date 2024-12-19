import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { styled } from "@mui/material";
import React from "react";
import { Carousel } from "react-responsive-carousel";
import "react-responsive-carousel/lib/styles/carousel.min.css";

import Button from "@mui/material/Button";
import ArrowNextIcon from "../../Icons/ArrowNextIcon";
import ArrowPrevIcon from "../../Icons/ArrowPrevIcon";

const ImgContainer = styled("div")(({ theme }) => ({
  width: "calc(100% - 8px)",
  height: 168,
  marginRight: 8,
  borderRadius: 10,
  overflow: "hidden",
  [theme.breakpoints.up(Breakpoint.Small)]: {
    height: 300,
  },
}));

const Img = styled("img")(() => ({
  objectFit: "cover",
  minHeight: "100%",
  width: "100%",
}));

const ArrowButton = styled(Button)(() => ({
  position: "absolute",
  zIndex: 2,
  top: "calc(50% - 15px)",
  cursor: "pointer",
  backgroundColor: "transparent",
  border: "none",
  padding: 0,
  minWidth: 0,
}));

const ArrowPrevButton = styled(ArrowButton)(() => ({
  left: 8,
}));

const ArrowNextButton = styled(ArrowButton)(() => ({
  right: 8,
}));

interface ImageCarouselProps {
  imgUrls: string[];
}

const ImageCarousel = ({ imgUrls }: ImageCarouselProps) => {
  return (
    <Carousel
      renderArrowPrev={(onClickHandler, hasPrev) =>
        hasPrev && (
          <ArrowPrevButton onClick={onClickHandler}>
            <ArrowPrevIcon />
          </ArrowPrevButton>
        )
      }
      renderArrowNext={(onClickHandler, hasNext) =>
        hasNext && (
          <ArrowNextButton onClick={onClickHandler}>
            <ArrowNextIcon />
          </ArrowNextButton>
        )
      }
      dynamicHeight={false}
      showIndicators={false}
      showStatus={false}
      showThumbs={false}
      centerSlidePercentage={80}
      centerMode
    >
      {imgUrls.map((url) => (
        <ImgContainer key={url}>
          <Img src={url} />
        </ImgContainer>
      ))}
    </Carousel>
  );
};

export default ImageCarousel;
