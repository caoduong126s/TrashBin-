"""
Test script for feedback and crowdsourcing endpoints
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_feedback():
    """Test feedback submission"""
    print("\n" + "=" * 60)
    print("Testing Feedback Endpoints")
    print("=" * 60)
    
    # Test submitting positive feedback
    print("\n1. Submitting positive feedback...")
    feedback_data = {
        "is_correct": True,
        "user_comment": "Phân loại chính xác!",
        "user_id": "test_user"
    }
    
    response = requests.post(f"{BASE_URL}/feedback/submit", json=feedback_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # Test submitting negative feedback
    print("\n2. Submitting negative feedback...")
    feedback_data = {
        "is_correct": False,
        "correct_class": "Nhựa",
        "user_comment": "Đây là nhựa chứ không phải giấy",
        "user_id": "test_user"
    }
    
    response = requests.post(f"{BASE_URL}/feedback/submit", json=feedback_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # Test getting feedback stats
    print("\n3. Getting feedback statistics...")
    response = requests.get(f"{BASE_URL}/feedback/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # Test getting recent feedback
    print("\n4. Getting recent feedback...")
    response = requests.get(f"{BASE_URL}/feedback/recent?limit=5")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_crowdsource():
    """Test crowdsourcing image submission"""
    print("\n" + "=" * 60)
    print("Testing Crowdsourcing Endpoints")
    print("=" * 60)
    
    # Find a test image (use any image from the project)
    test_image_path = Path(__file__).parent.parent / "models" / "test_image.jpg"
    
    # If test image doesn't exist, create a simple one
    if not test_image_path.exists():
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        test_image_path = Path(__file__).parent / "test_sample.jpg"
        img.save(test_image_path)
        print(f"Created test image at: {test_image_path}")
    
    # Test submitting image
    print("\n1. Submitting crowdsourced image...")
    
    with open(test_image_path, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        data = {
            'user_label': 'Nhựa',
            'user_id': 'test_user'
        }
        
        response = requests.post(f"{BASE_URL}/crowdsource/submit", files=files, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # Test getting crowdsource stats
    print("\n2. Getting crowdsourcing statistics...")
    response = requests.get(f"{BASE_URL}/crowdsource/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # Test getting crowdsourced images
    print("\n3. Getting crowdsourced images...")
    response = requests.get(f"{BASE_URL}/crowdsource/images?limit=5")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    print("\n Testing Feedback & Crowdsourcing Features")
    print("Make sure the backend server is running at http://127.0.0.1:8000\n")
    
    try:
        # Test health endpoint first
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(" Server is running!")
        else:
            print(" Server is not responding properly")
            exit(1)
        
        # Run tests
        test_feedback()
        test_crowdsource()
        
        print("\n" + "=" * 60)
        print(" All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n Error: Could not connect to server")
        print("Please make sure the backend is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
