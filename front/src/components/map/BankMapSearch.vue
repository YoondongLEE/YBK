<template>
  <div class="bank-map-container">
    <h2>가까운 은행 찾기</h2>
    <p class="description">출발지를 설정하고 근처 은행을 찾아보세요. 경로 안내도 확인할 수 있습니다.</p>
    
    <div class="search-filter-box">
      <h3>은행 찾기</h3>
      
      <div class="filter-row">
        <label>광역시/도</label>
        <select v-model="selectedRegion" class="filter-select" @change="updateDistricts">
          <option value="">선택하세요</option>
          <option v-for="region in regions" :key="region.name" :value="region.name">{{ region.name }}</option>
        </select>
      </div>
      
      <div class="filter-row">
        <label>시/군/구</label>
        <select v-model="selectedDistrict" class="filter-select" :disabled="!selectedRegion">
          <option value="">전체</option>
          <option v-for="district in availableDistricts" :key="district" :value="district">{{ district }}</option>
        </select>
      </div>
      
      <div class="filter-row">
        <label>은행</label>
        <select v-model="selectedBankType" class="filter-select">
          <option value="all">모든 금융기관</option>
          <option v-for="bank in banks" :key="bank" :value="bank">{{ bank }}</option>
        </select>
      </div>
      
      <button @click="searchByRegion" class="search-filter-btn">찾기</button>
    </div>
    
    <div class="search-controls">
      <div class="search-input-group">
        <label for="start-location">출발지:</label>
        <input 
          type="text" 
          id="start-location" 
          v-model="startLocation" 
          placeholder="출발 위치를 입력하세요"
          @keyup.enter="searchStartLocation"
        >
        <button @click="searchStartLocation" class="search-btn">
          <i class="fas fa-search"></i> 검색
        </button>
        <button @click="getCurrentLocation" class="current-location-btn" title="현재 위치 사용">
          <i class="fas fa-map-marker-alt"></i> 현재 위치
        </button>
      </div>
      
      <div class="search-options">
        <select v-model="searchRadius" class="radius-select">
          <option value="500">반경 500m</option>
          <option value="1000">반경 1km</option>
          <option value="2000">반경 2km</option>
          <option value="5000">반경 5km</option>
        </select>
      </div>
    </div>
    
    <div class="map-container">
      <div id="map" ref="mapContainer" style="width: 100%; height: 500px;"></div>
      
      <!-- 로딩 인디케이터 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
    
    <div v-if="selectedBank" class="bank-info-panel">
      <h3>{{ selectedBank.place_name }}</h3>
      <p><i class="fas fa-map-marker-alt"></i> {{ selectedBank.address_name }}</p>
      <p v-if="selectedBank.phone"><i class="fas fa-phone"></i> {{ selectedBank.phone }}</p>
      <p v-if="selectedBank.distance"><i class="fas fa-route"></i> 거리: {{ formatDistance(selectedBank.distance) }}</p>
      
      <div class="action-buttons">
        <button @click="showRoute" class="route-btn">
          <i class="fas fa-directions"></i> 길찾기
        </button>
        <button @click="closeInfoPanel" class="close-btn">
          <i class="fas fa-times"></i> 닫기
        </button>
      </div>
    </div>
    
    <div v-if="routeInfo" class="route-info-panel">
      <h3>경로 정보</h3>
      <p><i class="fas fa-walking"></i> 도보: {{ formatTime(routeInfo.walkingTime) }}</p>
      <p><i class="fas fa-road"></i> 거리: {{ formatDistance(routeInfo.distance) }}</p>
      <button @click="closeRoutePanel" class="close-btn">
        <i class="fas fa-times"></i> 닫기
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import mapData from '../../data/Map_data.json'; 


// 전역 스크립트 추가
const KAKAO_MAP_API_KEY = 'f6b597a2f64de8d3312748588885a960';
if (typeof document !== 'undefined') {
  const mapScript = document.createElement('script');
  mapScript.async = true;
  mapScript.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_MAP_API_KEY}&libraries=services,clusterer,drawing`;
  document.head.appendChild(mapScript);
}

export default {
  name: 'BankMapSearch',
  setup() {
    // 상태 변수
    const mapContainer = ref(null);
    const map = ref(null);
    const startLocation = ref('');
    const bankKeyword = ref('');
    const searchRadius = ref('1000');
    const selectedBank = ref(null);
    const routeInfo = ref(null);
    const markers = ref([]);
    const startMarker = ref(null);
    const polylines = ref([]);
    const currentLocation = ref(null);
    const loading = ref(false);
    const loadingMessage = ref('');

    // Map_data.json에서 데이터 로드
    const regions = ref(mapData.mapInfo || []);
    const banks = ref(mapData.bankInfo || []);

    // 지역 선택 필터
    const selectedRegion = ref('');
    const selectedDistrict = ref('');
    const selectedBankType = ref('all');
    
    // 선택한 지역에 따른 구/군 목록
    const availableDistricts = computed(() => {
      if (!selectedRegion.value) return [];
      const region = regions.value.find(r => r.name === selectedRegion.value);
      return region ? region.countries : [];
    });
    
    // 지역이 변경되면 구/군 초기화
    const updateDistricts = () => {
      selectedDistrict.value = '';
    };
    
    // 지역 기반 검색
    const searchByRegion = () => {
      if (!selectedRegion.value) {
        alert('광역시/도를 선택해주세요.');
        return;
      }
      
      // 검색어 구성
      let keyword = '';
      
      // 행정구역 추가
      if (selectedRegion.value) {
        keyword += selectedRegion.value;
        
        if (selectedDistrict.value) {
          keyword += ' ' + selectedDistrict.value;
        }
      }
      
      // 은행 추가
      if (selectedBankType.value !== 'all') {
        keyword += ' ' + selectedBankType.value;
      } else {
        keyword += ' 은행';
      }
      
      // 검색 실행
      searchByKeyword(keyword);
    };
    
    // 키워드로 검색
    const searchByKeyword = (keyword) => {
      if (!map.value) {
        alert('지도가 로드되지 않았습니다. 잠시 후 다시 시도해주세요.');
        return;
      }
      
      loading.value = true;
      loadingMessage.value = `'${keyword}' 검색 중...`;
      
      // 기존 마커와 경로선 제거
      clearMarkers();
      clearPolylines();
      
      // 선택된 은행 정보 초기화
      selectedBank.value = null;
      routeInfo.value = null;
      
      const places = new window.kakao.maps.services.Places();
      
      places.keywordSearch(keyword, (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          // 마커 추가
          result.forEach((place) => {
            addBankMarker(place);
          });
          
          // 경계 설정
          setBounds(result);
          
          loading.value = false;
        } else if (status === window.kakao.maps.services.Status.ZERO_RESULT) {
          loading.value = false;
          alert('검색 결과가 없습니다. 다른 키워드로 검색해보세요.');
        } else {
          loading.value = false;
          alert('검색 중 오류가 발생했습니다. 다시 시도해주세요.');
        }
      });
    };

    // 카카오맵 스크립트 로드 함수 수정
    const loadKakaoMapScript = () => {
      return new Promise((resolve, reject) => {
        if (window.kakao && window.kakao.maps) {
          resolve();
          return;
        }
        
        const script = document.createElement('script');
        // 하드코딩된 API 키 사용
        const apiKey = 'f6b597a2f64de8d3312748588885a960';
        console.log('카카오 API 키:', apiKey);
        
        // script.src는 한 번만 정의
        script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&libraries=services,clusterer,drawing&autoload=false`;
        
        script.onload = () => {
          window.kakao.maps.load(() => {
            console.log('카카오맵 API 로드 완료');
            resolve();
          });
        };
        script.onerror = (e) => {
          console.error('카카오맵 API 로드 실패:', e);
          reject(e);
        };
        document.head.appendChild(script);
      });
    };
    
    // 지도 초기화 함수 수정
    const initMap = () => {
      console.log('지도 초기화 시작');
      
      if (!mapContainer.value) {
        console.error('지도를 표시할 DOM 요소가 없습니다');
        return;
      }
      
      console.log('맵 컨테이너 DOM 확인:', mapContainer.value);
      
      // 카카오맵 로딩 확인 및 처리
      const waitForKakaoMaps = () => {
        console.log('카카오맵 로딩 체크');
        if (window.kakao && window.kakao.maps) {
          console.log('카카오맵 로딩 완료, 지도 생성 시작');
          
          // 명시적인 높이 설정
          mapContainer.value.style.height = '500px';
          mapContainer.value.style.width = '100%';
          
          try {
            const options = {
              center: new window.kakao.maps.LatLng(37.5665, 126.9780), // 서울 시청
              level: 5
            };
            
            map.value = new window.kakao.maps.Map(mapContainer.value, options);
            console.log('지도 생성 완료!');
            
            // 지도 컨트롤 추가
            const zoomControl = new window.kakao.maps.ZoomControl();
            map.value.addControl(zoomControl, window.kakao.maps.ControlPosition.RIGHT);
            
            // 현재 위치 가져오기
            getCurrentLocation();
          } catch (error) {
            console.error('지도 생성 중 오류:', error);
          }
        } else {
          console.log('카카오맵 아직 로딩 중...');
          setTimeout(waitForKakaoMaps, 300);
        }
      };
      
      // 카카오맵 로딩 체크 시작
      waitForKakaoMaps();
    };

    
    // 현재 위치 가져오기
    const getCurrentLocation = () => {
      if (!navigator.geolocation) {
        alert('브라우저가 위치 정보를 지원하지 않습니다.');
        return;
      }
      
      loading.value = true;
      loadingMessage.value = '현재 위치를 가져오는 중...';
      
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          
          currentLocation.value = {
            lat,
            lng
          };
          
          // 지도 중심 이동
          const moveLatLng = new window.kakao.maps.LatLng(lat, lng);
          map.value.setCenter(moveLatLng);
          
          // 출발지 마커 추가
          addStartMarker(moveLatLng);
          
          // 주소 정보 가져오기
          getAddressFromCoords(lat, lng, (address) => {
            startLocation.value = address;
            loading.value = false;
            
            // 주변 은행 자동 검색
            searchBanks();
          });
        },
        (error) => {
          loading.value = false;
          console.error('위치 정보를 가져오는데 실패했습니다:', error);
          alert('위치 정보를 가져오는데 실패했습니다. 출발지를 직접 입력해주세요.');
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0
        }
      );
    };
    
    // 좌표로 주소 정보 가져오기
    const getAddressFromCoords = (lat, lng, callback) => {
      const geocoder = new window.kakao.maps.services.Geocoder();
      
      geocoder.coord2Address(lng, lat, (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          if (result[0].road_address) {
            callback(result[0].road_address.address_name);
          } else {
            callback(result[0].address.address_name);
          }
        } else {
          callback('주소를 찾을 수 없습니다');
        }
      });
    };
    
    // 출발지 검색
    const searchStartLocation = () => {
      if (!startLocation.value) {
        alert('출발지를 입력해주세요.');
        return;
      }
      
      loading.value = true;
      loadingMessage.value = '출발지를 검색 중...';
      
      const geocoder = new window.kakao.maps.services.Geocoder();
      
      geocoder.addressSearch(startLocation.value, (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          const coords = new window.kakao.maps.LatLng(result[0].y, result[0].x);
          
          // 지도 중심 이동
          map.value.setCenter(coords);
          
          // 출발지 마커 추가
          addStartMarker(coords);
          
          // 현재 위치 저장
          currentLocation.value = {
            lat: result[0].y,
            lng: result[0].x
          };
          
          loading.value = false;
          
          // 주변 은행 자동 검색
          searchBanks();
        } else {
          loading.value = false;
          alert('출발지를 찾을 수 없습니다. 다른 주소를 입력해주세요.');
        }
      });
    };
    
    // 출발지 마커 추가
    const addStartMarker = (position) => {
      // 기존 마커 제거
      if (startMarker.value) {
        startMarker.value.setMap(null);
      }
      
      startMarker.value = new window.kakao.maps.Marker({
        position: position,
        map: map.value,
        zIndex: 10
      });
      
      // 인포윈도우 추가
      const infowindow = new window.kakao.maps.InfoWindow({
        content: '<div style="padding:5px;font-size:12px;">출발지</div>'
      });
      
      infowindow.open(map.value, startMarker.value);
      
      // 2초 후 인포윈도우 닫기
      setTimeout(() => {
        infowindow.close();
      }, 2000);
    };
    
    // searchBanks 함수 수정 (bankType.value를 selectedBankType.value로 변경)
    const searchBanks = () => {
      if (!currentLocation.value) {
        alert('출발지를 먼저 설정해주세요.');
        return;
      }
      
      loading.value = true;
      loadingMessage.value = '주변 은행을 검색 중...';
      
      // 기존 마커와 경로선 제거
      clearMarkers();
      clearPolylines();
      
      // 선택된 은행 정보 초기화
      selectedBank.value = null;
      routeInfo.value = null;
      
      const places = new window.kakao.maps.services.Places();
      
      // 검색 키워드 설정
      let keyword = '은행';
      
      // 특정 은행 선택된 경우
      if (selectedBankType.value !== 'all') {
        keyword = selectedBankType.value;
      }
      
      // 검색 옵션
      const options = {
        location: new window.kakao.maps.LatLng(currentLocation.value.lat, currentLocation.value.lng),
        radius: parseInt(searchRadius.value),
        sort: window.kakao.maps.services.SortBy.DISTANCE
      };
      
      places.keywordSearch(keyword, (result, status, pagination) => {
        if (status === window.kakao.maps.services.Status.OK) {
          // 마커 추가
          result.forEach((place) => {
            addBankMarker(place);
          });
          
          // 경계 설정
          setBounds(result);
          
          loading.value = false;
        } else if (status === window.kakao.maps.services.Status.ZERO_RESULT) {
          loading.value = false;
          alert('검색 결과가 없습니다. 다른 키워드나 더 넓은 반경으로 검색해보세요.');
        } else {
          loading.value = false;
          alert('검색 중 오류가 발생했습니다. 다시 시도해주세요.');
        }
      }, options);
    };
    
    // 은행 마커 추가
    const addBankMarker = (place) => {
      // 마커 이미지 설정
      const markerImage = new window.kakao.maps.MarkerImage(
        'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png',
        new window.kakao.maps.Size(24, 35)
      );
      
      const marker = new window.kakao.maps.Marker({
        position: new window.kakao.maps.LatLng(place.y, place.x),
        map: map.value,
        title: place.place_name,
        image: markerImage
      });
      
      markers.value.push(marker);
      
      // 마커 클릭 이벤트
      window.kakao.maps.event.addListener(marker, 'click', () => {
        selectBank(place);
      });
    };
    
    // 은행 선택
    const selectBank = (place) => {
      selectedBank.value = place;
      
      // 지도 중심 이동
      const moveLatLng = new window.kakao.maps.LatLng(place.y, place.x);
      map.value.setCenter(moveLatLng);
      
      // 인포윈도우 표시
      const infowindow = new window.kakao.maps.InfoWindow({
        content: `<div style="padding:5px;font-size:12px;width:200px;">${place.place_name}</div>`
      });
      
      // 기존 인포윈도우 모두 제거
      markers.value.forEach(marker => {
        infowindow.close(map.value, marker);
      });
      
      // 마커 찾기
      const marker = markers.value.find(m => 
        m.getPosition().getLat() === parseFloat(place.y) && 
        m.getPosition().getLng() === parseFloat(place.x)
      );
      
      if (marker) {
        infowindow.open(map.value, marker);
      }
    };
    
    // 경로 표시
    const showRoute = () => {
      if (!selectedBank.value || !currentLocation.value) {
        alert('출발지와 도착지가 모두 필요합니다.');
        return;
      }
      
      loading.value = true;
      loadingMessage.value = '경로를 계산 중...';
      
      // 기존 경로선 제거
      clearPolylines();
      
      // 직선 거리 계산
      const distance = calculateDistance(
        currentLocation.value.lat,
        currentLocation.value.lng,
        selectedBank.value.y,
        selectedBank.value.x
      );
      
      // 도보 시간 계산 (평균 시속 4km/h 기준)
      const walkingTime = Math.round((distance / 4) * 60);
      
      // 경로 정보 설정
      routeInfo.value = {
        distance,
        walkingTime
      };
      
      // 경로선 그리기
      const path = [
        new window.kakao.maps.LatLng(currentLocation.value.lat, currentLocation.value.lng),
        new window.kakao.maps.LatLng(selectedBank.value.y, selectedBank.value.x)
      ];
      
      const polyline = new window.kakao.maps.Polyline({
        path: path,
        strokeWeight: 5,
        strokeColor: '#5882FA',
        strokeOpacity: 0.7,
        strokeStyle: 'solid'
      });
      
      polyline.setMap(map.value);
      polylines.value.push(polyline);
      
      // 경계 설정
      const bounds = new window.kakao.maps.LatLngBounds();
      bounds.extend(path[0]);
      bounds.extend(path[1]);
      map.value.setBounds(bounds);
      
      loading.value = false;
    };
    
    // 거리 계산 (Haversine 공식)
    const calculateDistance = (lat1, lon1, lat2, lon2) => {
      const R = 6371; // 지구 반경 (km)
      const dLat = deg2rad(lat2 - lat1);
      const dLon = deg2rad(lon2 - lon1);
      const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
      const distance = R * c;
      return distance;
    };
    
    // 각도를 라디안으로 변환
    const deg2rad = (deg) => {
      return deg * (Math.PI/180);
    };
    
    // 경계 설정
    const setBounds = (places) => {
      const bounds = new window.kakao.maps.LatLngBounds();
      
      // 출발지 추가
      if (currentLocation.value) {
        bounds.extend(new window.kakao.maps.LatLng(
          currentLocation.value.lat,
          currentLocation.value.lng
        ));
      }
      
      // 결과 장소들 추가
      places.forEach(place => {
        bounds.extend(new window.kakao.maps.LatLng(place.y, place.x));
      });
      
      map.value.setBounds(bounds);
    };
    
    // 마커 제거
    const clearMarkers = () => {
      markers.value.forEach(marker => {
        marker.setMap(null);
      });
      markers.value = [];
    };
    
    // 경로선 제거
    const clearPolylines = () => {
      polylines.value.forEach(polyline => {
        polyline.setMap(null);
      });
      polylines.value = [];
    };
    
    // 패널 닫기
    const closeInfoPanel = () => {
      selectedBank.value = null;
    };
    
    const closeRoutePanel = () => {
      routeInfo.value = null;
      clearPolylines();
    };
    
    // 포맷팅 유틸리티
    const formatDistance = (distance) => {
      if (distance < 1) {
        return `${Math.round(distance * 1000)}m`;
      }
      return `${distance.toFixed(1)}km`;
    };
    
    const formatTime = (minutes) => {
      if (minutes < 60) {
        return `${minutes}분`;
      }
      const hours = Math.floor(minutes / 60);
      const remainMinutes = minutes % 60;
      return `${hours}시간 ${remainMinutes}분`;
    };
    
    // 컴포넌트 마운트 시 지도 초기화
    onMounted(() => {
      console.log('컴포넌트 마운트됨');
      // DOM이 완전히 렌더링될 시간을 주기 위해 약간의 지연 추가
      setTimeout(() => {
        initMap();
      }, 2000); // 2초로 증가
    });
    
    // 언마운트 시 자원 정리
    onUnmounted(() => {
      if (markers.value.length > 0) {
        markers.value.forEach(marker => {
          marker.setMap(null);
        });
      }
      
      if (polylines.value.length > 0) {
        polylines.value.forEach(polyline => {
          polyline.setMap(null);
        });
      }
    });
    
    return {
      mapContainer,
      startLocation,
      bankKeyword,
      searchRadius,
      selectedBankType,
      loading,
      loadingMessage,
      selectedBank,
      routeInfo,
      getCurrentLocation,
      searchStartLocation,
      searchBanks,
      showRoute,
      closeInfoPanel,
      closeRoutePanel,
      formatDistance,
      formatTime,
      // 지역 검색 필터 관련
      regions,
      banks,
      selectedRegion,
      selectedDistrict,
      availableDistricts,
      updateDistricts,
      searchByRegion,
      searchByKeyword
    };
  }
};
</script>

<style scoped>
.bank-map-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

h2 {
  margin-bottom: 10px;
  color: #333;
}

.description {
  color: #666;
  margin-bottom: 20px;
}

/* 검색 필터 스타일 - 사진과 유사하게 */
.search-filter-box {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.search-filter-box h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 15px 0;
  color: #333;
}

.filter-row {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.filter-row label {
  font-size: 14px;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

.filter-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
  width: 100%;
  font-size: 14px;
}

.search-filter-btn {
  width: 100%;
  padding: 10px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 10px;
  transition: background-color 0.3s;
}

.search-filter-btn:hover {
  background-color: #3a7bc8;
}

.search-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.search-input-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-input-group label {
  min-width: 80px;
  font-weight: 500;
  color: #555;
}

.search-input-group input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-btn {
  padding: 10px 15px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background-color: #3a7bc8;
}

.current-location-btn {
  padding: 10px 15px;
  background-color: #5cb85c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.current-location-btn:hover {
  background-color: #4cae4c;
}

.search-options {
  display: flex;
  gap: 15px;
}

.radius-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  flex: 1;
}

.map-container {
  position: relative;
  height: 500px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

#map {
  width: 100%;
  height: 100%;
  background-color: #f8f8f8; /* 지도가 로드되기 전에 보여줄 배경색 */
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.bank-info-panel,
.route-info-panel {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.bank-info-panel h3,
.route-info-panel h3 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.bank-info-panel p,
.route-info-panel p {
  margin: 5px 0;
  color: #555;
}

.bank-info-panel i,
.route-info-panel i {
  margin-right: 8px;
  color: #4a90e2;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.route-btn {
  padding: 8px 15px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  flex: 1;
}

.route-btn:hover {
  background-color: #3a7bc8;
}

.close-btn {
  padding: 8px 15px;
  background-color: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.close-btn:hover {
  background-color: #e0e0e0;
}

@media (max-width: 768px) {
  .search-input-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-input-group label {
    margin-bottom: 5px;
  }
  
  .search-options {
    flex-direction: column;
  }
  
  .map-container {
    height: 400px;
  }
  
  .filter-row {
    margin-bottom: 10px;
  }
}
</style>