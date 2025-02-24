import React from 'react';
import './HowDoesThisWork.css';

const HowDoesThisWork = ({ className = '', action = () => { }, children }) => {
    const handleMouseMove = (event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        // Calculate rotation (capped at 10 degrees)
        const rotateX = ((y - centerY) / centerY) * 10;
        const rotateY = ((x - centerX) / centerX) * 10;

        // Invert rotateX for a natural effect
        event.currentTarget.style.transform = `perspective(1000px) rotateX(${-rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
    };

    const resetTransform = (event) => {
        event.currentTarget.style.transform =
            'perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)';
    };

    const handleClick = () => {
        // Call the action passed in from the parent
        action();
    };

    return (
        <div
            className={`pop3d ${className} cta-div atkinson-hyperlegible-800`}
            onMouseMove={handleMouseMove}
            onMouseLeave={resetTransform}
            onClick={handleClick}
        >
            {children}
        </div>
    );
};

export default HowDoesThisWork;
