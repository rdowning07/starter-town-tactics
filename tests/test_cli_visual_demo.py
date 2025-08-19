"""
Tests for the CLI visual demo functionality.
"""
import pytest
from unittest.mock import Mock, patch

def test_visual_demo_import():
    """Test that the visual demo can be imported."""
    try:
        from cli.play_demo_visual import VisualDemo, main
        assert VisualDemo is not None
        assert main is not None
    except ImportError as e:
        pytest.skip(f"Visual demo not available: {e}")

@patch('pygame.init')
@patch('pygame.display.set_mode')
@patch('pygame.font.Font')
@patch('pygame.time.Clock')
def test_visual_demo_initialization(mock_clock, mock_font, mock_display, mock_init):
    """Test that VisualDemo can be initialized with mocked Pygame."""
    try:
        from cli.play_demo_visual import VisualDemo
        
        # Mock Pygame components
        mock_screen = Mock()
        mock_display.return_value = mock_screen
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance
        mock_clock_instance = Mock()
        mock_clock.return_value = mock_clock_instance
        
        # Create demo instance
        demo = VisualDemo()
        
        # Verify initialization
        assert demo.screen == mock_screen
        assert demo.clock == mock_clock_instance
        assert demo.font == mock_font_instance
        assert demo.running == True
        assert demo.tick_count == 0
        
    except ImportError as e:
        pytest.skip(f"Visual demo not available: {e}")

def test_visual_demo_state_loading():
    """Test that the demo can load game state."""
    try:
        from cli.play_demo_visual import VisualDemo
        from core.state import GameState
        
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.font.Font'), \
             patch('pygame.time.Clock'):
            
            demo = VisualDemo()
            state = demo.load_demo_state()
            
            # Verify state is created
            assert isinstance(state, GameState)
            
            # Verify units are added
            units = state.get_all_units()
            assert len(units) == 2
            
            # Check unit IDs
            unit_ids = [unit.id for unit in units]
            assert "player1" in unit_ids
            assert "enemy1" in unit_ids
            
    except ImportError as e:
        pytest.skip(f"Visual demo not available: {e}")

@patch('pygame.init')
@patch('pygame.display.set_mode')
@patch('pygame.font.Font')
@patch('pygame.time.Clock')
@patch('pygame.event.get')
@patch('pygame.display.flip')
@patch('pygame.quit')
def test_visual_demo_event_handling(mock_quit, mock_flip, mock_events, mock_clock, mock_font, mock_display, mock_init):
    """Test that the demo handles events correctly."""
    try:
        from cli.play_demo_visual import VisualDemo
        
        # Mock events to simulate quit
        mock_quit_event = Mock()
        mock_quit_event.type = 256  # pygame.QUIT value
        mock_events.return_value = [mock_quit_event]
        
        demo = VisualDemo()
        
        # Test event handling
        demo.handle_input()
        
        # Should set running to False when quit event is received
        assert demo.running == False
        
    except ImportError as e:
        pytest.skip(f"Visual demo not available: {e}")
