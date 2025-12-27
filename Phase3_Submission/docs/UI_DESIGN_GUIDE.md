# UI Design Guide

## Overview

SmartCommit features a modern web interface built with Streamlit, implementing Apple's iOS 26 "Liquid Glass" design language for a polished, professional user experience.

## Design Principles

### iOS 26 Liquid Glass Aesthetic

The interface follows Apple's latest design guidelines:

**Visual Characteristics:**
- Translucent panels with backdrop blur effects
- Content-focused layout with dynamic behavior
- Smooth gradients and glass-morphism effects
- Minimalist design with emphasis on functionality

**Typography:**
- Font: SF Pro Display / SF Pro Text
- Base size: 17px (iOS standard body text)
- Hierarchy through weight (Medium 500, Semibold 600, Bold 700)
- No all-caps styling for headers

**Color System:**
- Light mode: rgba(255,255,255,0.1-0.2) backgrounds
- Dark mode: rgba(21,21,21,0.4-0.5) backgrounds
- Blur radius: 15-25px for glass effect
- Border: 1-2px with rgba(255,255,255,0.2-0.4)
- Shadows: 0 8px 32px rgba(0,0,0,0.1-0.3)

## Interface Modes

### Generate Mode
Users can generate commit messages from code diffs:

**Input:**
- Text area for git diff input
- Supports unified diff format
- Real-time character count
- Automatic format detection

**Output:**
- AI-generated commit message
- Quality metrics display (BLEU, ROUGE, semantic similarity)
- Hallucination warnings (if detected)
- Confidence level indicator
- Copy-to-clipboard button

### Check Quality Mode
Users can evaluate existing commit messages:

**Input:**
- Git diff text area
- Commit message text area
- Compare against reference messages

**Output:**
- Detailed quality breakdown
- BLEU-4, ROUGE-L, semantic similarity scores
- Hallucination detection results
- Improvement suggestions
- Color-coded quality indicators

## UI Components

### Glass Panels
```css
background: rgba(255, 255, 255, 0.1);
backdrop-filter: blur(20px);
border: 1px solid rgba(255, 255, 255, 0.2);
border-radius: 12px;
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
```

### Quality Indicators
- **High Quality** (≥0.7): Green with checkmark icon
- **Medium Quality** (0.4-0.7): Yellow with warning icon
- **Low Quality** (<0.4): Red with alert icon

### Hallucination Warnings
- **Severity Levels**: None, Low, Medium, High, Critical
- **Visual Treatment**: Color-coded badges with icons
- **User Guidance**: Contextual help text and recommendations

## Accessibility Features

### WCAG 2.2 Compliance
- **Contrast Ratio**: Minimum 4.5:1 for text, 3:1 for UI components
- **Touch Targets**: Minimum 44×44px (Apple requirement)
- **Keyboard Navigation**: Full tab-accessible interface
- **Screen Reader Support**: ARIA labels on all interactive elements

### Accessibility Toggles
- **Reduced Motion**: Disables animations when `prefers-reduced-motion: reduce`
- **Reduced Transparency**: Solid backgrounds when enabled
- **High Contrast Mode**: Enhanced contrast for visibility
- **Font Scaling**: Respects user's browser font size preferences

## Performance Optimizations

### Animation Best Practices
- Never animate blur values directly (causes frame drops)
- Only animate `transform` and `opacity` (GPU-accelerated)
- Use `will-change` sparingly during animations only
- Pre-compute blur levels with CSS classes

### Browser Compatibility
- **Primary**: Chrome, Safari (full glass effect support)
- **Fallback**: Firefox, Edge (solid backgrounds with border)
- **Safari-specific**: `-webkit-backdrop-filter` prefix
- **GPU Acceleration**: `transform: translateZ(0)` for Safari

### Loading States
- Skeleton screens during API calls
- Progressive disclosure of content
- Optimistic UI updates
- Error boundaries for graceful failures

## User Experience Guidelines

### Workflow Optimization
1. **Minimal Input**: Users paste diff and click generate
2. **Instant Feedback**: Real-time validation and character counts
3. **Clear Results**: Easy-to-understand quality metrics
4. **Quick Actions**: Copy, regenerate, or adjust parameters

### Error Handling
- Friendly error messages (no technical jargon)
- Specific guidance for resolution
- Graceful degradation when API is unavailable
- Offline mode with cached responses (future)

### Responsive Design
- Desktop-first approach (primary use case)
- Tablet-friendly layout (iPad Pro)
- Mobile support (responsive breakpoints)
- Minimum resolution: 1024×768

## Implementation Details

### Streamlit Customization
- Custom CSS via `st.markdown()` with `unsafe_allow_html=True`
- Session state for mode switching
- Component caching for performance
- Custom theme configuration in `.streamlit/config.toml`

### CSS Architecture
```python
st.markdown("""
<style>
    .glass-panel {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 12px;
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)
```

## Future Enhancements

1. **Dark Mode Toggle**: User-selectable theme switching
2. **Diff Syntax Highlighting**: Color-coded diff visualization
3. **History Panel**: View previous generations
4. **Settings Panel**: Customize model parameters
5. **Keyboard Shortcuts**: Power user features (Cmd+Enter to generate)
6. **Export Options**: Save results as JSON, CSV, or PDF
