$(document).ready(function() {
	// Инициализация параметров из URL
	function getUrlParameter(name) {
		const urlParams = new URLSearchParams(window.location.search);
		return urlParams.get(name);
	}

	// Загружаем параметры из URL при инициализации
	const urlSalon = getUrlParameter('salon');
	const urlMaster = getUrlParameter('master');
	const urlService = getUrlParameter('service');
	const urlDate = getUrlParameter('date');
	const urlTime = getUrlParameter('time');

	let selected = {
		salon: null,
		master: null,
		service: null,
		date: null,
		time: null
	};

	let availableDates = [];

	if (urlSalon) selected.salon = urlSalon;
	if (urlMaster) selected.master = urlMaster;
	if (urlService) selected.service = urlService;
	if (urlDate) selected.date = urlDate;
	if (urlTime) selected.time = urlTime;

	function updateSalons(reset = false) {
		$.get('/api/salons/', {
			master: selected.master,
			service: selected.service,
			date: selected.date
		}, function(data) {
			let html = '';
			let ids = [];
			data.forEach(function(salon) {
				html += `<div class="accordion__block fic salon-item" data-id="${salon.id}">
					<div class="accordion__block_intro">${salon.name}</div>
					<div class="accordion__block_address">${salon.address}</div>
				</div>`;
				ids.push(String(salon.id));
			});
			$('.salons-panel').html(html);
			// Сбрасываем выбор салона только если reset=true и салон недоступен
			if (reset && selected.salon && !ids.includes(String(selected.salon))) {
				selected.salon = null;
				$('.service__salons button.accordion').text('(Выберите салон)');
			}
			// Восстанавливаем выделение, если выбранный салон доступен
			if (selected.salon && !reset) {
				$(`.salon-item[data-id='${selected.salon}']`).addClass('selected');
			}
		});
	}

	function updateMasters(reset = false) {
		$.get('/api/masters/', {
			salon: selected.salon,
			service: selected.service,
			date: selected.date
		}, function(data) {
			let html = '';
			let ids = [];
			data.forEach(function(master) {
				html += `<div class="accordion__block fic master-item" data-id="${master.id}">
					<div class="accordion__block_master">${master.name}</div>
				</div>`;
				ids.push(String(master.id));
			});
			$('.masters-panel').html(html);
			// Сбрасываем выбор мастера только если reset=true и мастер недоступен
			if (reset && selected.master && !ids.includes(String(selected.master))) {
				selected.master = null;
				$('.service__masters button.accordion').text('(Выберите мастера)');
			}
			// Восстанавливаем выделение, если выбранный мастер доступен
			if (selected.master && !reset) {
				$(`.master-item[data-id='${selected.master}']`).addClass('selected');
			}
		});
	}

	function updateServices(reset = false) {
		$.get('/api/services/', {
			salon: selected.salon,
			master: selected.master,
			date: selected.date
		}, function(data) {
			let html = '';
			let ids = [];
			data.forEach(function(service) {
				html += `<div class="accordion__block_item fic service-item" data-id="${service.id}">
					<div class="accordion__block_item_intro">${service.name}</div>
					<div class="accordion__block_item_address">${service.price ? service.price + ' ₽' : ''}</div>
				</div>`;
				ids.push(String(service.id));
			});
			$('.services-panel').html(html);
			// Сбрасываем выбор услуги только если reset=true и услуга недоступна
			if (reset && selected.service && !ids.includes(String(selected.service))) {
				selected.service = null;
				$('.service__services button.accordion').text('(Выберите услугу)');
			}
			// Восстанавливаем выделение, если выбранная услуга доступна
			if (selected.service && !reset) {
				$(`.service-item[data-id='${selected.service}']`).addClass('selected');
			}
		});
	}

	function updateTimeslots() {
		if (!selected.salon || !selected.master || !selected.service || !selected.date) {
			$('.timeslots-panel').html('<div>Выберите все параметры для отображения времени</div>');
			return;
		}
		$.get('/api/timeslots/', {
			salon: selected.salon,
			master: selected.master,
			service: selected.service,
			date: selected.date
		}, function(data) {
			let html = '';
			if (data.free_slots.length === 0) {
				html = '<div>Нет свободных слотов</div>';
			} else {
				data.free_slots.forEach(function(slot) {
					html += `<button data-time="${slot}" class="time__elems_btn">${slot}</button>`;
				});
			}
			$('.timeslots-panel').html(html);
			// Восстанавливаем выбор времени, если оно было выбрано и доступно
			if (selected.time && data.free_slots.includes(selected.time)) {
				$(`.time__elems_btn[data-time='${selected.time}']`).addClass('active');
			}
		});
	}

	function updateAvailableDates() {
		$.get('/api/dates/', {
			salon: selected.salon,
			master: selected.master
		}, function(data) {
			availableDates = data.available_dates || [];
			if (window.datepickerInstance) {
				window.datepickerInstance.update({
					isDateDisabled: function(date) {
						const year = date.getFullYear();
						const month = String(date.getMonth() + 1).padStart(2, '0');
						const day = String(date.getDate()).padStart(2, '0');
						const d = `${year}-${month}-${day}`;
						return !availableDates.includes(d);
					}
				});
				// Проверяем, доступна ли текущая выбранная дата
				if (selected.date && !availableDates.includes(selected.date)) {
					selected.date = null;
					window.datepickerInstance.clear();
				}
			}
		});
	}

	// Инициализация
	updateSalons(true);
	updateMasters(true);
	updateServices(true);
	updateAvailableDates();
	
	// Если параметры загружены из URL, обновляем соответствующие данные
	if (urlSalon || urlMaster || urlService || urlDate) {
		updateTimeslots();
		updateNextButton();
		
		// Визуально выделяем выбранные элементы после загрузки данных
		setTimeout(function() {
			if (selected.salon) {
				$(`.salon-item[data-id='${selected.salon}']`).addClass('selected');
				var salonName = $(`.salon-item[data-id='${selected.salon}']`).find('.accordion__block_intro').text();
				$('.service__form_block').each(function() {
					if ($(this).find('.salon-item').length > 0) {
						$(this).find('button.accordion').text(salonName);
					}
				});
			}
			if (selected.master) {
				$(`.master-item[data-id='${selected.master}']`).addClass('selected');
				var masterName = $(`.master-item[data-id='${selected.master}']`).find('.accordion__block_master').text();
				$('.service__form_block').each(function() {
					if ($(this).find('.master-item').length > 0) {
						$(this).find('button.accordion').text(masterName);
					}
				});
			}
			if (selected.service) {
				$(`.service-item[data-id='${selected.service}']`).addClass('selected');
				var serviceName = $(`.service-item[data-id='${selected.service}']`).find('.accordion__block_item_intro').text();
				var servicePrice = $(`.service-item[data-id='${selected.service}']`).find('.accordion__block_item_address').text();
				$('.service__form_block').each(function() {
					if ($(this).find('.service-item').length > 0) {
						$(this).find('button.accordion').text(serviceName + (servicePrice ? ' — ' + servicePrice : ''));
					}
				});
			}
			if (selected.time) {
				$(`.time__elems_btn[data-time='${selected.time}']`).addClass('active');
			}
		}, 500); // Небольшая задержка для загрузки данных
	}

	// События выбора
	$(document).on('click', '.salon-item', function() {
		selected.salon = $(this).data('id');
		$('.salon-item').removeClass('selected');
		$(this).addClass('selected');
		// Обновляем текст кнопки-аккордеона
		var name = $(this).find('.accordion__block_intro').text();
		var btn = $(this).closest('.service__form_block').find('button.accordion');
		btn.text(name);
		// Закрываем панель
		$(this).closest('.panel').removeClass('active');
		// Обновляем остальные данные, не сбрасывая выбор
		updateMasters(false);
		updateServices(false);
		updateTimeslots();
		updateAvailableDates();
		updateNextButton();
	});

	$(document).on('click', '.master-item', function() {
		// Сначала фиксируем выбор мастера
		selected.master = $(this).data('id');
		// Обновляем текст кнопки-аккордеона
		var name = $(this).find('.accordion__block_master').text();
		var btn = $(this).closest('.service__form_block').find('button.accordion');
		btn.text(name);
		// Визуально выделяем выбранный элемент
		$('.master-item').removeClass('selected');
		$(this).addClass('selected');
		// Закрываем панель
		$(this).closest('.panel').removeClass('active');
		// Обновляем остальные данные, не сбрасывая выбор мастера
		updateSalons(false);
		updateServices(false);
		updateTimeslots();
		updateAvailableDates();
		updateNextButton();
	});

	$(document).on('click', '.service-item', function() {
		selected.service = $(this).data('id');
		$('.service-item').removeClass('selected');
		$(this).addClass('selected');
		// Обновляем текст кнопки-аккордеона
		var name = $(this).find('.accordion__block_item_intro').text();
		var price = $(this).find('.accordion__block_item_address').text();
		var btn = $(this).closest('.service__form_block').find('button.accordion');
		btn.text(name + (price ? ' — ' + price : ''));
		// Закрываем панель
		$(this).closest('.panel').removeClass('active');
		// Обновляем остальные данные, не сбрасывая выбор
		updateMasters(false);
		updateSalons(false);
		updateTimeslots();
		updateNextButton();
	});

	// Дата
	window.datepickerInstance = new AirDatepicker('#datepickerHere', {
		onSelect({date}) {
			if (date) {
				// Используем более безопасный метод форматирования даты
				const year = date.getFullYear();
				const month = String(date.getMonth() + 1).padStart(2, '0');
				const day = String(date.getDate()).padStart(2, '0');
				selected.date = `${year}-${month}-${day}`;
				// Обновляем списки без сброса текущих выборов
				updateSalons(false);
				updateMasters(false);
				updateServices(false);
				updateTimeslots();
				updateNextButton();
			}
		},
		isDateDisabled: function(date) {
			if (availableDates.length === 0) return false;
			// Используем тот же метод форматирования
			const year = date.getFullYear();
			const month = String(date.getMonth() + 1).padStart(2, '0');
			const day = String(date.getDate()).padStart(2, '0');
			const d = `${year}-${month}-${day}`;
			return !availableDates.includes(d);
		}
	});

	// Время
	$(document).on('click', '.time__elems_btn', function() {
		$('.time__elems_btn').removeClass('active');
		$(this).addClass('active');
		selected.time = $(this).data('time');
		updateNextButton();
	});

	$('.salonsSlider').slick({
		arrows: true,
	  slidesToShow: 4,
	  prevArrow: $('.salons .leftArrow'),
	  nextArrow: $('.salons .rightArrow'),
	  responsive: [
	  	{
	      breakpoint: 1199,
	      settings: {
	        

	        slidesToShow: 3
	      }
	    },
	    {
	      breakpoint: 991,
	      settings: {
	        

	        slidesToShow: 2
	      }
	    },
	    {
	      breakpoint: 575,
	      settings: {
	        slidesToShow: 1
	      }
	    }
	  ]
	});
	$('.servicesSlider').slick({
		arrows: true,
	  slidesToShow: 4,
	  prevArrow: $('.services .leftArrow'),
	  nextArrow: $('.services .rightArrow'),
	  responsive: [
	  	{
	      breakpoint: 1199,
	      settings: {
	        

	        slidesToShow: 3
	      }
	    },
	    {
	      breakpoint: 991,
	      settings: {
	        
	      	centerMode: true,
  			//centerPadding: '60px',
	        slidesToShow: 2
	      }
	    },
	    {
	      breakpoint: 575,
	      settings: {
	        slidesToShow: 1
	      }
	    }
	  ]
	});

	$('.mastersSlider').slick({
		arrows: true,
	  slidesToShow: 4,
	  prevArrow: $('.masters .leftArrow'),
	  nextArrow: $('.masters .rightArrow'),
	  responsive: [
	  	{
	      breakpoint: 1199,
	      settings: {
	        

	        slidesToShow: 3
	      }
	    },
	    {
	      breakpoint: 991,
	      settings: {
	        

	        slidesToShow: 2
	      }
	    },
	    {
	      breakpoint: 575,
	      settings: {
	        slidesToShow: 1
	      }
	    }
	  ]
	});

	$('.reviewsSlider').slick({
		arrows: true,
	  slidesToShow: 4,
	  prevArrow: $('.reviews .leftArrow'),
	  nextArrow: $('.reviews .rightArrow'),
	  responsive: [
	  	{
	      breakpoint: 1199,
	      settings: {
	        

	        slidesToShow: 3
	      }
	    },
	    {
	      breakpoint: 991,
	      settings: {
	        

	        slidesToShow: 2
	      }
	    },
	    {
	      breakpoint: 575,
	      settings: {
	        slidesToShow: 1
	      }
	    }
	  ]
	});

	// menu
	$('.header__mobMenu').click(function() {
		$('#mobMenu').show()
	})
	$('.mobMenuClose').click(function() {
		$('#mobMenu').hide()
	})

	var acc = document.getElementsByClassName("accordion");
	var i;

	for (i = 0; i < acc.length; i++) {
	  acc[i].addEventListener("click", function(e) {
	  	e.preventDefault()
	    this.classList.toggle("active");
	    var panel = $(this).next()
	    panel.hasClass('active') ?  
	    	 panel.removeClass('active')
	    	: 
	    	 panel.addClass('active')
	  });
	}

	//popup
	$('.header__block_auth').click(function(e) {
		e.preventDefault()
		$('#authModal').arcticmodal();
		// $('#confirmModal').arcticmodal();

	})

	$('.rewiewPopupOpen').click(function(e) {
		e.preventDefault()
		$('#reviewModal').arcticmodal();
	})
	$('.payPopupOpen').click(function(e) {
		e.preventDefault()
		$('#paymentModal').arcticmodal();
	})
	$('.tipsPopupOpen').click(function(e) {
		e.preventDefault()
		$('#tipsModal').arcticmodal();
	})
	
	$('.authPopup__form').submit(function() {
		$('#confirmModal').arcticmodal();
		return false
	})

	//service
	$('.time__items .time__elems_elem .time__elems_btn').click(function(e) {
		e.preventDefault()
		$('.time__elems_btn').removeClass('active')
		$(this).addClass('active')
		// $(this).hasClass('active') ? $(this).removeClass('active') : $(this).addClass('active')
	})

	$(document).on('click', '.servicePage', function() {
		if($('.time__items .time__elems_elem .time__elems_btn').hasClass('active') && $('.service__form_block > button').hasClass('selected')) {
			$('.time__btns_next').addClass('active')
		}
	})
	

	function updateNextButton() {
		if (selected.salon && selected.master && selected.service && selected.date && selected.time) {
			$('.time__btns_next').prop('disabled', false).addClass('active');
		} else {
			$('.time__btns_next').prop('disabled', true).removeClass('active');
		}
	}

	$(document).on('click', '.salon-item, .master-item, .service-item, .time__elems_btn', function() {
		updateNextButton();
	});
	$(document).on('change', '#datepickerHere', function() {
		updateNextButton();
	});

	// При клике на Далее, если все параметры выбраны, переход на service-finally
	$(document).on('click', '.time__btns_next', function(e) {
		if (!$(this).hasClass('active')) {
			e.preventDefault();
			return;
		}
		const params = $.param(selected);
		window.location.href = `/service-finally/?${params}`;
	});

	// Обработка кнопок "Записаться" на главной странице
	$(document).on('click', '.masters__footer_btn', function(e) {
		e.preventDefault();
		const masterBlock = $(this).closest('.masters__block');
		const masterId = masterBlock.find('.masters__header_name').data('master-id');
		
		if (masterId) {
			// Переходим на страницу service с предвыбранным мастером
			window.location.href = `/service/?master=${masterId}`;
		} else {
			// Если ID мастера не найден, просто переходим на страницу service
			window.location.href = '/service/';
		}
	});

	// После выбора мастера или салона обновляем доступные даты
	$(document).on('click', '.salon-item, .master-item', function() {
		updateAvailableDates();
	});

})