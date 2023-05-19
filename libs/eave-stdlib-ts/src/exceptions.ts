export class HTTPException extends Error {
  statusCode: number;

  constructor(statusCode: number, message: string = '') {
    super(message);
    Object.setPrototypeOf(this, HTTPException.prototype);
    this.statusCode = statusCode;
  }
}



export class BadRequestError extends HTTPException {
  constructor(message: string = '') {
    super(400, message);
    Object.setPrototypeOf(this, BadRequestError.prototype);
  }
}


export class UnauthorizedError extends HTTPException {
  constructor(message: string = '') {
    super(401, message);
    Object.setPrototypeOf(this, UnauthorizedError.prototype);
  }
}

export class NotFoundError extends HTTPException {
  constructor(message: string = '') {
    super(404, message);
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}

export class InternalServerError extends HTTPException {
  constructor(message: string = '') {
    super(500, message);
    Object.setPrototypeOf(this, InternalServerError.prototype);
  }
}


export class InvalidAuthError extends UnauthorizedError {
  constructor(message: string = '') {
    super(message);
    Object.setPrototypeOf(this, InvalidAuthError.prototype);
  }
}

export class InvalidJWTError extends UnauthorizedError {
  constructor(message: string = '') {
    super(message);
    Object.setPrototypeOf(this, InvalidJWTError.prototype);
  }
}

export class AccessTokenExpiredError extends UnauthorizedError {
  constructor(message: string = '') {
    super(message);
    Object.setPrototypeOf(this, AccessTokenExpiredError.prototype);
  }
}

export class InvalidSignatureError extends BadRequestError {
  constructor(message: string = '') {
    super(message);
    Object.setPrototypeOf(this, InvalidSignatureError.prototype);
  }
}

export class InvalidStateError extends BadRequestError {
  constructor(message: string = '') {
    super(message);
    Object.setPrototypeOf(this, InvalidStateError.prototype);
  }
}

export class MissingRequiredHeaderError extends BadRequestError {
  constructor(message: string = '') {
    super(message);
    Object.setPrototypeOf(this, MissingRequiredHeaderError.prototype);
  }
}

export class MaxRetryAttemptsReachedError extends InternalServerError {
  constructor(message: string = '') {
    super(message);
    Object.setPrototypeOf(this, MaxRetryAttemptsReachedError.prototype);
  }
}

export class InvalidChecksumError extends InternalServerError {
  constructor(message: string = '') {
    super(message);
    Object.setPrototypeOf(this, InvalidChecksumError.prototype);
  }
}

export class DataConflictError extends BadRequestError {
  constructor(message: string = '') {
    super(message);
    Object.setPrototypeOf(this, DataConflictError.prototype);
  }
}
