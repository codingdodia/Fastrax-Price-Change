import React from 'react';
import 'bootstrap/dist/css/bootstrap.css';











function Message() {

    const user = { name: 'John Doe' };
    return <h1>Hello, {user.name}!</h1>;
}

export const FastraxPosLoginForm = () => {
    return (
        <Form>
            <Form.Group controlId="formBasicEmail">
                <Form.Label>Email address</Form.Label>
                <Form.Control type="email" placeholder="Enter email" />
            </Form.Group>
        </Form>
    );
}


export default Message;
