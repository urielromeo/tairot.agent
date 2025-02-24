import React from 'react';
import './Pop3D.css';

const Pop3D = ({ className = '', action = '', children }) => {
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

    const handleClick = (event) => {
        if (action === 'scroll-to-learn-more') {
            const target = document.getElementById('learn-more');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        } else if (action === 'back-to-tairot-agent') {
            window.location.href = 'https://tairot.soniclords.com';
        } else if (action === 'open-contract') {
            window.location.href = 'https://sonicscan.org/address/0x2c4a44a1a45e059b685fe49ee63023d9c7f770cf';
        }
    };

    return (
        <div
            className={`pop3d ${className} cta-div w-100 atkinson-hyperlegible-800`}
            onMouseMove={handleMouseMove}
            onMouseLeave={resetTransform}
            onClick={handleClick}
        >
            {children}
        </div>
    );
};

export default Pop3D;
