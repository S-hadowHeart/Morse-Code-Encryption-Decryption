class AudioManager {
    constructor() {
        this.audioContext = null;
        this.sounds = {};
        this.enabled = true;
    }

    async init() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            await this.loadSounds();
        } catch (error) {
            console.error('Failed to initialize audio:', error);
        }
    }

    async loadSounds() {
        const soundFiles = {
            dot: '/static/sounds/dot.mp3',
            dash: '/static/sounds/dash.mp3',
            notification: '/static/sounds/notification.mp3',
            click: '/static/sounds/click.mp3'
        };

        for (const [name, url] of Object.entries(soundFiles)) {
            try {
                const response = await fetch(url);
                const arrayBuffer = await response.arrayBuffer();
                const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
                this.sounds[name] = audioBuffer;
            } catch (error) {
                console.error(`Failed to load sound ${name}:`, error);
            }
        }
    }

    playSound(name, options = {}) {
        if (!this.enabled || !this.audioContext || !this.sounds[name]) return;

        const source = this.audioContext.createBufferSource();
        source.buffer = this.sounds[name];

        const gainNode = this.audioContext.createGain();
        gainNode.gain.value = options.volume || 1;

        source.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        source.start(0);
    }

    playMorseCode(text) {
        if (!this.enabled || !text) return;

        const dotDuration = 100;
        const dashDuration = dotDuration * 3;
        const pauseDuration = dotDuration;
        
        let currentTime = 0;
        
        for (const char of text) {
            setTimeout(() => {
                if (char === '.') {
                    this.playSound('dot', { volume: 0.5 });
                } else if (char === '-') {
                    this.playSound('dash', { volume: 0.5 });
                }
            }, currentTime);

            if (char === '.') {
                currentTime += dotDuration + pauseDuration;
            } else if (char === '-') {
                currentTime += dashDuration + pauseDuration;
            } else if (char === ' ') {
                currentTime += pauseDuration * 3;
            } else if (char === '/') {
                currentTime += pauseDuration * 7;
            }
        }
    }

    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }
}