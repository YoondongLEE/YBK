<template>
  <div class="bank-map-container">
    <div class="filters-container">
      <!-- 지역 기반 검색 -->
      <div class="region-search-container">
        <h3>지역으로 찾기</h3>
        
        <div class="region-filters">
          <div class="filter-row">
            <select v-model="selectedRegion" @change="updateDistricts" class="filter-select">
              <option value="">광역시/도 선택</option>
              <option v-for="region in regions" :key="region.name" :value="region.name">
                {{ region.name }}
              </option>
            </select>
            
            <select v-model="selectedDistrict" class="filter-select" :disabled="!selectedRegion">
              <option value="">구/군 선택 (선택사항)</option>
              <option v-for="district in availableDistricts" :key="district" :value="district">
                {{ district }}
              </option>
            </select>
          </div>
          
          <div class="filter-row">
            <select v-model="selectedBankType" class="filter-select">
              <option value="all">모든 은행</option>
              <option v-for="bank in banks" :key="bank" :value="bank">
                {{ bank }}
              </option>
            </select>
            
            <button @click="searchByRegion" class="search-btn">
              <i class="fas fa-search"></i> 찾기
            </button>
          </div>
        </div>
      </div>
      
      <!-- 위치 기반 검색 -->
      <div class="location-search-container">
        <h3>현재 위치/주소로 찾기</h3>
        
        <div class="location-filters">
          <div class="filter-row">
            <input 
              v-model="startLocation" 
              placeholder="출발지 주소 또는 키워드 입력" 
              class="location-input"
            />
            
            <button @click="getCurrentLocation" class="location-btn">
              <i class="fas fa-location-arrow"></i> 현재 위치
            </button>
            
            <button @click="searchStartLocation" class="search-btn">
              <i class="fas fa-search"></i> 검색
            </button>
          </div>
          
          <div class="filter-row">
            <select v-model="selectedBankType" class="filter-select">
              <option value="all">모든 은행</option>
              <option v-for="bank in banks" :key="bank" :value="bank">
                {{ bank }}
              </option>
            </select>
            
            <select v-model="searchRadius" class="filter-select">
              <option value="500">500m</option>
              <option value="1000">1km</option>
              <option value="2000">2km</option>
              <option value="3000">3km</option>
              <option value="5000">5km</option>
            </select>
            
            <button @click="searchBanks" class="search-btn">
              <i class="fas fa-search"></i> 주변 검색
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 지도 표시 영역 -->
    <div ref="mapContainer" class="map-container"></div>
    
    <!-- 로딩 표시 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>{{ loadingMessage }}</p>
    </div>
    
    <!-- 선택된 은행 정보 -->
    <div v-if="selectedBank" class="bank-info-panel">
      <h3>{{ selectedBank.place_name }}</h3>
      <p><i class="fas fa-map-marker-alt"></i> {{ selectedBank.address_name }}</p>
      <p v-if="selectedBank.phone"><i class="fas fa-phone"></i> {{ selectedBank.phone }}</p>
      <p v-if="selectedBank.place_url">
        <i class="fas fa-link"></i>
        <a :href="selectedBank.place_url" target="_blank">상세 정보</a>
      </p>
      
      <div class="action-buttons">
        <button @click="closeInfoPanel" class="close-btn">
          <i class="fas fa-times"></i> 닫기
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import mapData from '../../data/Map_data.json'; 

// 전역 스크립트 추가 - 환경 변수 사용
const KAKAO_MAP_API_KEY = import.meta.env.VITE_KAKAO_JAVASCRIPT_KEY;
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
    const markers = ref([]);
    const startMarker = ref(null);
    const currentLocation = ref(null);
    const loading = ref(false);
    const loadingMessage = ref('');
    
    // 현재 열린 인포윈도우를 추적하는 변수
    const currentInfowindow = ref(null);

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
      
      // 선택된 은행 정보 초기화
      selectedBank.value = null;
      
      // 현재 인포윈도우가 있으면 닫기
      if (currentInfowindow.value) {
        currentInfowindow.value.close();
        currentInfowindow.value = null;
      }
      
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

    // 카카오맵 스크립트 로드 함수 - 환경 변수 사용
    const loadKakaoMapScript = () => {
      return new Promise((resolve, reject) => {
        if (window.kakao && window.kakao.maps) {
          resolve();
          return;
        }
        
        const script = document.createElement('script');
        // 환경 변수에서 API 키 가져오기
        const apiKey = import.meta.env.VITE_KAKAO_JAVASCRIPT_KEY;
        console.log('카카오 API 키 로드됨');
        
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
          
          loading.value = false;
          
          // 주변 은행 검색
          searchBanks();
          
          // 주소 가져오기
          const geocoder = new window.kakao.maps.services.Geocoder();
          geocoder.coord2Address(lng, lat, (result, status) => {
            if (status === window.kakao.maps.services.Status.OK) {
              const addr = result[0].address.address_name;
              startLocation.value = addr;
            }
          });
        },
        (error) => {
          console.error('위치 정보 가져오기 실패:', error);
          loading.value = false;
          alert('위치 정보를 가져오는데 실패했습니다. 주소를 직접 입력해주세요.');
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    };
    
    // 출발지 주소로 검색 - 키워드 검색으로 개선
    const searchStartLocation = () => {
      if (!startLocation.value) {
        alert('출발지 주소나 키워드를 입력해주세요.');
        return;
      }
      
      if (!map.value) {
        alert('지도가 로드되지 않았습니다. 잠시 후 다시 시도해주세요.');
        return;
      }
      
      loading.value = true;
      loadingMessage.value = '출발지 검색 중...';
      
      // 키워드 검색으로 변경
      const places = new window.kakao.maps.services.Places();
      places.keywordSearch(startLocation.value, (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          // 첫 번째 결과를 기준으로 위치 설정
          const place = result[0];
          const coords = new window.kakao.maps.LatLng(place.y, place.x);
          
          // 지도 중심 이동
          map.value.setCenter(coords);
          
          // 출발지 마커 추가
          addStartMarker(coords);
          
          // 현재 위치 저장
          currentLocation.value = {
            lat: place.y,
            lng: place.x
          };
          
          loading.value = false;
          
          // 선택한 위치 표시
          startLocation.value = place.address_name || place.place_name;
          
          // 주변 은행 자동 검색
          searchBanks();
        } else {
          loading.value = false;
          alert('출발지를 찾을 수 없습니다. 다른 키워드로 검색해보세요.');
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
        alert('현재 위치 정보가 없습니다. 위치 정보를 먼저 가져와주세요.');
        return;
      }
      
      if (!map.value) {
        alert('지도가 로드되지 않았습니다. 잠시 후 다시 시도해주세요.');
        return;
      }
      
      // 은행 키워드 구성
      let keyword = selectedBankType.value === 'all' ? '은행' : selectedBankType.value;
      
      loading.value = true;
      loadingMessage.value = `반경 ${searchRadius.value}m 내 ${keyword} 검색 중...`;
      
      // 기존 마커 제거
      clearMarkers();
      
      // 선택된 은행 정보 초기화
      selectedBank.value = null;
      
      // 수정: 현재 인포윈도우가 있으면 닫기
      if (currentInfowindow.value) {
        currentInfowindow.value.close();
        currentInfowindow.value = null;
      }
      
      // 장소 검색 객체 생성
      const places = new window.kakao.maps.services.Places();
      
      // 검색 옵션
      const options = {
        location: new window.kakao.maps.LatLng(currentLocation.value.lat, currentLocation.value.lng),
        radius: searchRadius.value,
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
      
      // 마커 클릭 이벤트 - 수정된 부분
      window.kakao.maps.event.addListener(marker, 'click', () => {
        selectBank(place, marker);
      });
    };
    
    // 은행 선택 - 수정된 부분
    const selectBank = (place, marker) => {
      selectedBank.value = place;
      
      // 지도 중심 이동
      const moveLatLng = new window.kakao.maps.LatLng(place.y, place.x);
      map.value.setCenter(moveLatLng);
      
      // 기존 인포윈도우가 있으면 닫기
      if (currentInfowindow.value) {
        currentInfowindow.value.close();
      }
      
      // 인포윈도우 생성 및 표시
      const infowindow = new window.kakao.maps.InfoWindow({
        content: `
          <div style="padding:10px;width:250px;">
            <h4 style="margin:0 0 5px;font-size:14px;">${place.place_name}</h4>
            <p style="margin:0;font-size:12px;line-height:1.5;">
              주소: ${place.address_name}<br/>
              ${place.phone ? '전화: ' + place.phone : ''}
            </p>
          </div>
        `,
        removable: true
      });
      
      // 인포윈도우 표시
      infowindow.open(map.value, marker);
      
      // 현재 인포윈도우 저장
      currentInfowindow.value = infowindow;
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
    
    // 패널 닫기
    const closeInfoPanel = () => {
      selectedBank.value = null;
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
      
      // 수정: 인포윈도우가 있으면 닫기
      if (currentInfowindow.value) {
        currentInfowindow.value.close();
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
      getCurrentLocation,
      searchStartLocation,
      searchBanks,
      closeInfoPanel,
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
  width: 100%;
  position: relative;
}

.filters-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.region-search-container,
.location-search-container {
  width: 100%;
}

h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #333;
}

.filter-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.filter-select {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.location-input {
  flex: 2;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-btn, 
.location-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-btn {
  background-color: #4285f4;
  color: white;
}

.search-btn:hover {
  background-color: #3367d6;
}

.location-btn {
  background-color: #34a853;
  color: white;
}

.location-btn:hover {
  background-color: #2e8f49;
}

.map-container {
  width: 100%;
  height: 500px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* 로딩 애니메이션 */
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255,255,255,0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  border: 6px solid #f3f3f3;
  border-top: 6px solid #4285f4;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 선택된 은행 정보 패널 */
.bank-info-panel {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  max-width: 300px;
  z-index: 2;
}

.bank-info-panel h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 18px;
}

.bank-info-panel p {
  margin: 5px 0;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.close-btn {
  background-color: #ea4335;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
}

/* 반응형 스타일 */
@media screen and (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    gap: 5px;
  }
  
  .bank-info-panel {
    left: 10px;
    right: 10px;
    max-width: calc(100% - 20px);
  }
}
</style>