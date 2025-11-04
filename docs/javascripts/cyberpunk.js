// Cyberpunk theme enhancements

document.addEventListener('DOMContentLoaded', function() {
  // Add neon pulse to status badges
  const badges = document.querySelectorAll('.md-typeset p');
  badges.forEach(badge => {
    const text = badge.textContent;
    if (text.includes('🧪 Experimental') || text.includes('✅ Stable') || text.includes('🚧 In Progress')) {
      badge.classList.add('neon-pulse');
    }
  });

  // Customize Mermaid diagram theme
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
      theme: 'dark',
      themeVariables: {
        primaryColor: '#ff00ff',
        primaryTextColor: '#e0e0e0',
        primaryBorderColor: '#00ffff',
        lineColor: '#00ffff',
        secondaryColor: '#9d00ff',
        tertiaryColor: '#0a0a0a',
        background: '#1a1a1a',
        mainBkg: '#1a1a1a',
        secondBkg: '#0a0a0a',
        textColor: '#e0e0e0',
        border1: '#ff00ff',
        border2: '#00ffff',
        fontSize: '16px'
      }
    });
  }

  // Add glitch effect to page title on hover
  const pageTitle = document.querySelector('.md-header__topic');
  if (pageTitle) {
    pageTitle.addEventListener('mouseenter', function() {
      this.style.animation = 'glitch 0.3s ease-in-out';
    });
  }

  // Console easter egg
  console.log('%c🌟 FANTASTIC ENGINE 🌟', 'color: #ff00ff; font-size: 20px; font-weight: bold; text-shadow: 0 0 10px #ff00ff;');
  console.log('%cWelcome to the experiment playground!', 'color: #00ffff; font-size: 14px;');
  console.log('%cBuilt with Claude Code ⚡', 'color: #9d00ff; font-size: 12px;');
});

// Add glitch animation
const style = document.createElement('style');
style.textContent = `
  @keyframes glitch {
    0% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
    100% { transform: translate(0); }
  }
`;
document.head.appendChild(style);
