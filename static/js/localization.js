const translations = {
    'en': {
        'nav_dashboard': 'Dashboard',
        'nav_scanner': 'AI Crop Scanner',
        'nav_recommendations': 'Crop Recommendations',
        'nav_weather': 'Weather & Map',
        'nav_irrigation': 'Smart Irrigation',
        'nav_alerts': 'Alert Center',
        'nav_store': 'Agri Store',
        'nav_chatbot': '🤖 AI Assistant',
        'nav_mandi': 'Mandi Rates',
        'nav_logout': 'Logout',
        'btn_profile': 'Profile',
        'lbl_connecting': '● Connecting...'
    },
    'hi': {
        'nav_dashboard': 'डैशबोर्ड',
        'nav_scanner': 'एआई फसल स्कैनर',
        'nav_recommendations': 'फसल की सिफारिशें',
        'nav_weather': 'मौसम और नक्शा',
        'nav_irrigation': 'स्मार्ट सिंचाई',
        'nav_alerts': 'अलर्ट केंद्र',
        'nav_store': 'कृषि स्टोर',
        'nav_chatbot': '🤖 एआई सहायक',
        'nav_mandi': 'मंडी भाव',
        'nav_logout': 'लॉग आउट',
        'btn_profile': 'प्रोफ़ाइल',
        'lbl_connecting': '● कनेक्ट हो रहा है...'
    },
    'pa': {
        'nav_dashboard': 'ਡੈਸ਼ਬੋਰਡ',
        'nav_scanner': 'ਏਆਈ ਫਸਲ ਸਕੈਨਰ',
        'nav_recommendations': 'ਫਸਲ ਦੀਆਂ ਸਿਫ਼ਾਰਸ਼ਾਂ',
        'nav_weather': 'ਮੌਸਮ ਅਤੇ ਨਕਸ਼ਾ',
        'nav_irrigation': 'ਸਮਾਰਟ ਸਿੰਚਾਈ',
        'nav_alerts': 'ਅਲਰਟ ਸੈਂਟਰ',
        'nav_store': 'ਐਗਰੀ ਸਟੋਰ',
        'nav_chatbot': '🤖 ਏਆਈ ਸਹਾਇਕ',
        'nav_mandi': 'ਮੰਡੀ ਦੇ ਭਾਅ',
        'nav_logout': 'ਲਾਗ ਆਉਟ',
        'btn_profile': 'ਪ੍ਰੋਫਾਈਲ',
        'lbl_connecting': '● ਜੁੜ ਰਿਹਾ ਹੈ...'
    },
    'mr': {
        'nav_dashboard': 'डॅशबोर्ड',
        'nav_scanner': 'एआय पीक स्कॅनर',
        'nav_recommendations': 'पीक शिफारसी',
        'nav_weather': 'हवामान आणि नकाशा',
        'nav_irrigation': 'स्मार्ट सिंचन',
        'nav_alerts': 'अॅलर्ट सेंटर',
        'nav_store': 'कृषी स्टोअर',
        'nav_chatbot': '🤖 एआय सहाय्यक',
        'nav_mandi': 'मंडी भाव',
        'nav_logout': 'लॉग आउट',
        'btn_profile': 'प्रोफाइल',
        'lbl_connecting': '● कनेक्ट करत आहे...'
    }
};

function changeLanguage(lang) {
    localStorage.setItem('agriLanguage', lang);
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            if (el.tagName === 'INPUT' && el.type === 'button') {
                el.value = translations[lang][key];
            } else {
                el.textContent = translations[lang][key];
            }
        }
    });
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('agriLanguage') || 'en';
    const langSelect = document.getElementById('language-select');
    if (langSelect) {
        langSelect.value = savedLang;
    }
    changeLanguage(savedLang);
});
