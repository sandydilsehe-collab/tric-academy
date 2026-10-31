// TRIC Academy - Client Interactions & Form Logic

document.addEventListener('DOMContentLoaded', function() {
  initMobileNav();
  initDateOfBirthAndAge();
  initPhotoUploadPreview();
  initSponsorshipToggle();
  initDeclarationAutoFill();
  initMockOtpModal();
  initCompetitionCharts();
  initPhotoLightbox();
  initAdminQuickApprove();
});

// 1. Date of Birth, Age Calculation & Single Digit Boxes
function initDateOfBirthAndAge() {
  const dobPicker = document.getElementById('dobPicker');
  const ageDisplay = document.getElementById('ageDisplay');
  const ageInput = document.getElementById('ageInput');
  const minorSection = document.getElementById('minorSection');
  const seniorNotice = document.getElementById('seniorNotice');
  const guardianInput = document.getElementById('guardianInput');
  const occupationInput = document.getElementById('occupationInput');

  const digitBoxes = [
    document.getElementById('d1'), document.getElementById('d2'),
    document.getElementById('m1'), document.getElementById('m2'),
    document.getElementById('y1'), document.getElementById('y2'),
    document.getElementById('y3'), document.getElementById('y4')
  ];

  if (!dobPicker) return;

  function updateFromDate(dateStr) {
    if (!dateStr) return;
    const parts = dateStr.split('-');
    if (parts.length !== 3) return;

    const y = parts[0];
    const m = parts[1];
    const d = parts[2];

    // Populate digit boxes DD MM YYYY
    if (digitBoxes[0] && d.length === 2) {
      digitBoxes[0].textContent = d[0];
      digitBoxes[1].textContent = d[1];
    }
    if (digitBoxes[2] && m.length === 2) {
      digitBoxes[2].textContent = m[0];
      digitBoxes[3].textContent = m[1];
    }
    if (digitBoxes[4] && y.length === 4) {
      digitBoxes[4].textContent = y[0];
      digitBoxes[5].textContent = y[1];
      digitBoxes[6].textContent = y[2];
      digitBoxes[7].textContent = y[3];
    }

    // Calculate age
    const birthDate = new Date(y, parseInt(m, 10) - 1, d);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }

    if (age >= 0 && age < 120) {
      if (ageDisplay) ageDisplay.textContent = age;
      if (ageInput) ageInput.value = age;

      // Minor rules (< 18)
      if (minorSection) {
        if (age < 18) {
          minorSection.style.display = 'flex';
          if (guardianInput) guardianInput.required = true;
          if (occupationInput) occupationInput.required = true;
        } else {
          minorSection.style.display = 'none';
          if (guardianInput) guardianInput.required = false;
          if (occupationInput) occupationInput.required = false;
        }
      }

      // Senior rules (> 50)
      if (seniorNotice) {
        seniorNotice.style.display = age > 50 ? 'block' : 'none';
      }
    }
  }

  dobPicker.addEventListener('change', function(e) {
    updateFromDate(e.target.value);
  });

  // Initial calculation if editing existing or prefilled
  if (dobPicker.value) {
    updateFromDate(dobPicker.value);
  }
}

// 2. Photo Upload Preview
function initPhotoUploadPreview() {
  const photoInput = document.getElementById('photoInput');
  const photoContainer = document.getElementById('photoContainer');
  const photoPreview = document.getElementById('photoPreview');
  const photoPlaceholder = document.getElementById('photoPlaceholder');

  if (!photoInput || !photoContainer) return;

  photoContainer.addEventListener('click', function() {
    photoInput.click();
  });

  photoInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Passport photo size must be under 5MB.');
        photoInput.value = '';
        return;
      }
      const reader = new FileReader();
      reader.onload = function(evt) {
        if (photoPreview) {
          photoPreview.src = evt.target.result;
          photoPreview.style.display = 'block';
        }
        if (photoPlaceholder) {
          photoPlaceholder.style.display = 'none';
        }
      };
      reader.readAsDataURL(file);
    }
  });
}

// 3. Department Sponsorship Toggle
function initSponsorshipToggle() {
  const sponsoredYes = document.getElementById('sponsoredYes');
  const sponsoredNo = document.getElementById('sponsoredNo');
  const sponsorUploadWrap = document.getElementById('sponsorUploadWrap');
  const sponsorFileInput = document.getElementById('sponsorFileInput');

  if (!sponsoredYes || !sponsorUploadWrap) return;

  function toggleSponsor() {
    if (sponsoredYes.checked) {
      sponsorUploadWrap.style.display = 'block';
      if (sponsorFileInput) sponsorFileInput.required = true;
    } else {
      sponsorUploadWrap.style.display = 'none';
      if (sponsorFileInput) sponsorFileInput.required = false;
    }
  }

  sponsoredYes.addEventListener('change', toggleSponsor);
  if (sponsoredNo) sponsoredNo.addEventListener('change', toggleSponsor);
  toggleSponsor();
}

// 4. Auto-fill Declaration Name and Signature
function initDeclarationAutoFill() {
  const applicantNameInput = document.getElementById('applicantNameInput');
  const declarationNameSpan = document.getElementById('declarationNameSpan');
  const signatureInput = document.getElementById('signatureInput');

  if (!applicantNameInput) return;

  if (signatureInput) {
    signatureInput.addEventListener('input', function() {
      signatureInput.dataset.manuallyEdited = 'true';
    });
  }

  applicantNameInput.addEventListener('input', function(e) {
    const name = e.target.value.trim();
    if (declarationNameSpan) {
      declarationNameSpan.textContent = name || '____________________';
    }
    if (signatureInput && (!signatureInput.dataset.manuallyEdited || !signatureInput.value.trim())) {
      signatureInput.value = name;
    }
  });
}

// 5. Robust Public Form Validation and Simulated Mock OTP Flow
function initMockOtpModal() {
  const applicationForm = document.getElementById('applicationForm');
  const submitFormBtn = document.getElementById('submitFormBtn');
  const otpModal = document.getElementById('otpModal');
  const otpCodeDisplay = document.getElementById('otpCodeDisplay');
  const otpInputField = document.getElementById('otpInputField');
  const autoFillOtpBtn = document.getElementById('autoFillOtpBtn');
  const verifyOtpBtn = document.getElementById('verifyOtpBtn');
  const otpErrorMsg = document.getElementById('otpErrorMsg');

  if (!applicationForm || window._applicationFormScriptLoaded) return;

  const isPublicSignup = applicationForm.getAttribute('data-is-public') === 'true';

  function showValidationError(msg, targetInput) {
    const errBanner = document.getElementById('formValidationError');
    const errMsg = document.getElementById('formValidationMsg');
    if (errBanner && errMsg) {
      errMsg.textContent = msg;
      errBanner.style.display = 'block';
      errBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      alert(msg);
    }
    if (targetInput) {
      try {
        targetInput.focus();
        targetInput.style.outline = '2px solid #EF4444';
        targetInput.style.borderColor = '#EF4444';
        setTimeout(() => {
          targetInput.style.outline = '';
          targetInput.style.borderColor = '';
        }, 3500);
      } catch (_) {}
    }
  }

  function validatePublicForm() {
    // 1. Applicant Name
    const nameInput = document.getElementById('applicantNameInput');
    if (!nameInput || !nameInput.value.trim()) {
      showValidationError('Please enter the Name of the Applicant.', nameInput);
      return false;
    }

    // 2. Address
    const addressInput = document.getElementById('addressInput');
    if (!addressInput || !addressInput.value.trim()) {
      showValidationError('Please enter your residential Address.', addressInput);
      return false;
    }

    // 3. Pincode
    const pincodeInput = document.querySelector('input[name="pincode"]');
    if (!pincodeInput || !pincodeInput.value.trim()) {
      showValidationError('Please enter your Pin Code (e.g. 641652).', pincodeInput);
      return false;
    }

    // 4. Contact No
    const phoneInput = document.getElementById('phoneInput');
    if (!phoneInput || !phoneInput.value.trim()) {
      showValidationError('Please enter your 10-digit mobile Contact Number.', phoneInput);
      return false;
    }
    const cleanPhone = phoneInput.value.trim().replace(/\D/g, '');
    if (cleanPhone.length < 10) {
      showValidationError('Contact Number must be a valid 10-digit phone number.', phoneInput);
      return false;
    }

    // 5. Email ID
    const emailInput = document.getElementById('emailInput');
    if (!emailInput || !emailInput.value.trim() || !emailInput.value.includes('@')) {
      showValidationError('Please enter a valid Email ID.', emailInput);
      return false;
    }

    // 6. Date of Birth
    const dobPicker = document.getElementById('dobPicker');
    if (!dobPicker || !dobPicker.value) {
      showValidationError('Please select your Date of Birth.', dobPicker);
      return false;
    }

    // 7. Minor validations (< 18 yrs)
    const ageVal = parseInt(document.getElementById('ageInput')?.value || '99', 10);
    if (!isNaN(ageVal) && ageVal < 18) {
      const guardianInput = document.getElementById('guardianInput');
      const occupationInput = document.getElementById('occupationInput');
      if (!guardianInput || !guardianInput.value.trim()) {
        showValidationError('Parent / Guardian Name is mandatory for minor applicants (under 18).', guardianInput);
        return false;
      }
      if (!occupationInput || !occupationInput.value.trim()) {
        showValidationError('Parent / Guardian Occupation is mandatory for minor applicants.', occupationInput);
        return false;
      }
    }

    // 8. Password for member login
    const passwordInput = document.getElementById('passwordInput');
    if (passwordInput && passwordInput.value.length < 6) {
      showValidationError('Please create an account password with at least 6 characters.', passwordInput);
      return false;
    }

    // 9. Health Declaration
    const healthDeclared = document.getElementById('healthDeclared');
    if (healthDeclared && !healthDeclared.checked) {
      showValidationError('Please confirm the Health Declaration checkbox.', healthDeclared);
      return false;
    }

    // 10. Mandatory 32 Rules & Regulations confirmation
    const rulesAgreed = document.getElementById('rulesAgreed');
    if (rulesAgreed && !rulesAgreed.checked) {
      showValidationError('Mandatory Requirement: You must read and accept all 32 Rules & Regulations.');
      if (typeof openRulesModal === 'function') {
        openRulesModal();
      }
      return false;
    }

    // 11. Signature Name
    const signatureInput = document.getElementById('signatureInput');
    if (signatureInput && !signatureInput.value.trim()) {
      signatureInput.value = nameInput.value.trim();
    }

    // Hide any previous validation banner
    const errBanner = document.getElementById('formValidationError');
    if (errBanner) errBanner.style.display = 'none';

    return true;
  }

  function submitFormDirectly() {
    const btn = document.getElementById('submitFormBtn');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Submitting Application...';
    }
    HTMLFormElement.prototype.submit.call(applicationForm);
  }

  function handleFormSubmission(e) {
    if (e && e.preventDefault) e.preventDefault();

    if (!isPublicSignup) {
      // Admin mode: direct submission
      HTMLFormElement.prototype.submit.call(applicationForm);
      return;
    }

    if (!validatePublicForm()) {
      return;
    }

    const phoneVerified = document.getElementById('phoneVerifiedFlag');
    if (phoneVerified) {
      phoneVerified.value = '1';
    }
    const mockOtpField = document.getElementById('mockOtpField');
    if (mockOtpField) {
      mockOtpField.value = '123456';
    }

    submitFormDirectly();
  }

  // Hook submit button click
  if (submitFormBtn) {
    submitFormBtn.addEventListener('click', handleFormSubmission);
  }

  // Hook native form submit
  applicationForm.addEventListener('submit', handleFormSubmission);

  // Hook Auto-Fill OTP button
  if (autoFillOtpBtn) {
    autoFillOtpBtn.addEventListener('click', function() {
      if (otpInputField && window._currentMockOtp) {
        otpInputField.value = window._currentMockOtp;
      }
    });
  }

  // Hook OTP verification confirmation
  if (verifyOtpBtn) {
    verifyOtpBtn.addEventListener('click', function() {
      const entered = otpInputField ? otpInputField.value.trim() : '';
      if (entered === window._currentMockOtp || !entered || entered === otpCodeDisplay?.textContent) {
        const phoneVerified = document.getElementById('phoneVerifiedFlag');
        const mockOtpField = document.getElementById('mockOtpField');
        if (phoneVerified) phoneVerified.value = '1';
        if (mockOtpField) mockOtpField.value = window._currentMockOtp || entered;
        if (otpModal) otpModal.style.display = 'none';
        submitFormDirectly();
      } else {
        if (otpErrorMsg) {
          otpErrorMsg.style.display = 'block';
          otpErrorMsg.textContent = 'Incorrect OTP code. Enter ' + window._currentMockOtp;
        }
      }
    });
  }
}

// 6. Competition Charts using Chart.js
function initCompetitionCharts() {
  const chartCanvas = document.getElementById('swimmerProgressChart');
  if (!chartCanvas || typeof Chart === 'undefined') return;

  const rawData = chartCanvas.getAttribute('data-records');
  if (!rawData) return;

  try {
    const records = JSON.parse(rawData);
    if (!records || records.length === 0) return;

    // Group by stroke
    const strokes = {};
    records.forEach(r => {
      const label = `${r.distance} ${r.stroke}`;
      if (!strokes[label]) strokes[label] = [];
      strokes[label].push({
        x: r.meet_date,
        y: r.time_seconds,
        display: r.time_display,
        meet: r.meet_name
      });
    });

    const colors = ['#0284C7', '#1F8A8A', '#D97706', '#9333EA', '#DC2626'];
    let cIdx = 0;

    const datasets = Object.keys(strokes).map(label => {
      const color = colors[cIdx % colors.length];
      cIdx++;
      return {
        label: label.toUpperCase(),
        data: strokes[label].map(d => ({ x: d.x, y: d.y })),
        borderColor: color,
        backgroundColor: color,
        borderWidth: 2,
        tension: 0.2,
        pointRadius: 5,
        pointHoverRadius: 7
      };
    });

    new Chart(chartCanvas, {
      type: 'line',
      data: { datasets: datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: { display: true, text: 'Competition Meet Date' }
          },
          y: {
            title: { display: true, text: 'Race Time (Seconds)' },
            beginAtZero: false
          }
        },
        plugins: {
          legend: { position: 'top' },
          tooltip: {
            callbacks: {
              label: function(context) {
                const sec = context.parsed.y;
                const mins = Math.floor(sec / 60);
                const rem = (sec % 60).toFixed(2);
                const disp = mins > 0 ? `${mins}:${rem.padStart(5, '0')}` : `${rem}s`;
                return `${context.dataset.label}: ${disp}`;
              }
            }
          }
        }
      }
    });
  } catch (err) {
    console.error('Failed to parse competition chart data', err);
  }
}


// 7. Responsive Mobile Navigation Drawer & Hamburger Toggle
function initMobileNav() {
  const hamburgerBtn = document.getElementById('navHamburgerBtn');
  const closeBtn = document.getElementById('mobileNavCloseBtn');
  const mobileNavMenu = document.getElementById('mobileNavMenu');
  const backdrop = document.getElementById('mobileNavBackdrop');

  if (!hamburgerBtn || !mobileNavMenu) return;

  function openMenu() {
    hamburgerBtn.classList.add('is-active');
    hamburgerBtn.setAttribute('aria-expanded', 'true');
    mobileNavMenu.classList.add('is-open');
    mobileNavMenu.setAttribute('aria-hidden', 'false');
    if (backdrop) backdrop.classList.add('is-open');
    document.body.classList.add('nav-open');
  }

  function closeMenu() {
    hamburgerBtn.classList.remove('is-active');
    hamburgerBtn.setAttribute('aria-expanded', 'false');
    mobileNavMenu.classList.remove('is-open');
    mobileNavMenu.setAttribute('aria-hidden', 'true');
    if (backdrop) backdrop.classList.remove('is-open');
    document.body.classList.remove('nav-open');
  }

  function toggleMenu() {
    if (mobileNavMenu.classList.contains('is-open')) {
      closeMenu();
    } else {
      openMenu();
    }
  }

  hamburgerBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    toggleMenu();
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      closeMenu();
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', closeMenu);
  }

  // Close when tapping any link inside mobile menu
  const links = mobileNavMenu.querySelectorAll('a');
  links.forEach(function(link) {
    link.addEventListener('click', function() {
      closeMenu();
    });
  });

  // Close on Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && mobileNavMenu.classList.contains('is-open')) {
      closeMenu();
    }
  });

  // Close on desktop resize
  window.addEventListener('resize', function() {
    if (window.innerWidth >= 992 && mobileNavMenu.classList.contains('is-open')) {
      closeMenu();
    }
  });
}


// ==========================================================================
// Interactive Photo Lightbox (Expand on Click or Touch)
// ==========================================================================
function initPhotoLightbox() {
  const modal = document.getElementById('photoLightboxModal');
  if (!modal) return;

  const backdrop = document.getElementById('photoLightboxBackdrop');
  const closeBtn = document.getElementById('photoLightboxCloseBtn');
  const prevBtn = document.getElementById('photoLightboxPrevBtn');
  const nextBtn = document.getElementById('photoLightboxNextBtn');
  const imgElement = document.getElementById('photoLightboxImg');
  const titleElement = document.getElementById('photoLightboxTitle');
  const tagElement = document.getElementById('photoLightboxTag');
  const captionElement = document.getElementById('photoLightboxCaption');
  const counterElement = document.getElementById('photoLightboxCounter');
  const fullscreenBtn = document.getElementById('photoLightboxFullscreenBtn');

  // Collect all gallery items
  const items = Array.from(document.querySelectorAll('[data-expandable="true"]'));
  if (items.length === 0) return;

  let currentIndex = 0;

  function updateLightbox(index) {
    if (index < 0) index = items.length - 1;
    if (index >= items.length) index = 0;
    currentIndex = index;

    const item = items[currentIndex];
    const src = item.getAttribute('data-img-src') || item.querySelector('img')?.src;
    const title = item.getAttribute('data-title') || item.querySelector('h4')?.textContent || 'TRIC Academy Facility';
    const tag = item.getAttribute('data-category') || 'Academy Photo';
    const caption = item.getAttribute('data-caption') || item.querySelector('p')?.textContent || '';

    if (imgElement) {
      imgElement.style.opacity = '0.3';
      imgElement.src = src;
      imgElement.alt = title;
      imgElement.onload = function() {
        imgElement.style.opacity = '1';
      };
    }

    if (titleElement) titleElement.textContent = title;
    if (tagElement) tagElement.textContent = tag;
    if (captionElement) captionElement.textContent = caption;
    if (counterElement) counterElement.textContent = `Photo ${currentIndex + 1} of ${items.length}`;
  }

  function openLightbox(index) {
    updateLightbox(index);
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.documentElement.style.overflow = '';
    document.body.style.overflow = '';
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {});
    }
  }

  function showNext() {
    updateLightbox(currentIndex + 1);
  }

  function showPrev() {
    updateLightbox(currentIndex - 1);
  }

  // Bind click & touch listeners to gallery items
  items.forEach(function(item, idx) {
    // Click or touch anywhere on the photo preview
    item.addEventListener('click', function(e) {
      e.preventDefault();
      openLightbox(idx);
    });

    // Keyboard support: Enter / Space to open
    item.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openLightbox(idx);
      }
    });
  });

  // Also bind to explicit card expand buttons
  document.querySelectorAll('.photo-expand-trigger-btn').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      const idx = parseInt(btn.getAttribute('data-index') || '0', 10);
      openLightbox(idx);
    });
  });

  // Modal control buttons
  if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
  if (backdrop) backdrop.addEventListener('click', closeLightbox);
  if (prevBtn) prevBtn.addEventListener('click', function(e) { e.stopPropagation(); showPrev(); });
  if (nextBtn) nextBtn.addEventListener('click', function(e) { e.stopPropagation(); showNext(); });

  // Fullscreen button
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      if (!document.fullscreenElement) {
        modal.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });
  }

  // Keyboard navigation: Escape to close, Left/Right arrows to navigate
  document.addEventListener('keydown', function(e) {
    if (!modal.classList.contains('is-open')) return;
    if (e.key === 'Escape') {
      closeLightbox();
    } else if (e.key === 'ArrowRight') {
      showNext();
    } else if (e.key === 'ArrowLeft') {
      showPrev();
    }
  });

  // Mobile Touch Gestures: Swipe left (next), Swipe right (prev), Swipe down (close)
  let touchStartX = 0;
  let touchStartY = 0;
  let touchEndX = 0;
  let touchEndY = 0;

  modal.addEventListener('touchstart', function(e) {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
  }, { passive: true });

  modal.addEventListener('touchend', function(e) {
    touchEndX = e.changedTouches[0].screenX;
    touchEndY = e.changedTouches[0].screenY;
    handleTouchGesture();
  }, { passive: true });

  function handleTouchGesture() {
    const diffX = touchEndX - touchStartX;
    const diffY = touchEndY - touchStartY;

    // Horizontal swipe threshold: 45px
    if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 45) {
      if (diffX < 0) {
        showNext(); // Swipe left
      } else {
        showPrev(); // Swipe right
      }
    } else if (diffY > 90) {
      // Swiping downwards closes modal
      closeLightbox();
    }
  }

  // Support standalone expandable photos across any page (e.g. member ID or pass)
  document.querySelectorAll('.expandable-photo').forEach(function(photo) {
    photo.style.cursor = 'zoom-in';
    photo.addEventListener('click', function(e) {
      e.preventDefault();
      if (imgElement) {
        imgElement.src = photo.src;
        imgElement.alt = photo.alt || 'Expanded Photo';
      }
      if (titleElement) titleElement.textContent = photo.alt || 'Photo View';
      if (tagElement) tagElement.textContent = 'TRIC Academy';
      if (captionElement) captionElement.textContent = '';
      if (counterElement) counterElement.textContent = 'Photo View';
      modal.classList.add('is-open');
      modal.setAttribute('aria-hidden', 'false');
      document.documentElement.style.overflow = 'hidden';
      document.body.style.overflow = 'hidden';
    });
  });
}


// ==========================================================================
// Super Admin 1-Click Pass Approval & Live Counters Update
// ==========================================================================
function initAdminQuickApprove() {
  // Quick approve from tables (Recent Pending Applications / Pending Applicants)
  document.querySelectorAll('.quick-approve-form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const btn = form.querySelector('.approve-pass-btn');
      const userId = form.getAttribute('data-user-id');
      if (!btn || btn.disabled) return;

      btn.disabled = true;
      const originalText = btn.innerHTML;
      btn.innerHTML = '⏳ Approving...';
      btn.style.opacity = '0.7';

      fetch(form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          // Permanently disable the button for this user
          btn.innerHTML = '✓ Pass Approved &amp; Issued';
          btn.classList.remove('btn-primary');
          btn.classList.add('btn-success');
          btn.style.backgroundColor = '#10B981';
          btn.style.borderColor = '#059669';
          btn.style.color = '#FFFFFF';
          btn.style.opacity = '0.85';
          btn.style.cursor = 'not-allowed';
          btn.disabled = true;

          // Update row status badge if present
          const badge = document.getElementById(`status-badge-${userId}`);
          if (badge) {
            badge.className = 'status-badge status-active';
            badge.textContent = '✓ Approved';
          }

          // Update pending stat counter on dashboard
          const pendingStat = document.getElementById('pendingApprovalStat');
          if (pendingStat && typeof data.pending_users !== 'undefined') {
            pendingStat.textContent = data.pending_users;
          }

          // Update header counters
          const heroCount = document.getElementById('heroPendingCount');
          if (heroCount && typeof data.pending_users !== 'undefined') {
            heroCount.textContent = data.pending_users;
          }

          const headerCount = document.getElementById('pendingCountHeader');
          if (headerCount && typeof data.pending_users !== 'undefined') {
            headerCount.textContent = data.pending_users;
          }

          // Show confirmation toast
          showApprovalToast(data.message || `Pass approved & issued for ${data.name}! (ID: ${data.id_card_number})`);
        } else {
          btn.disabled = false;
          btn.innerHTML = originalText;
          btn.style.opacity = '1';
          alert(data.message || 'Error processing approval');
        }
      })
      .catch(err => {
        console.error('Quick approve error:', err);
        form.submit(); // fallback to normal submit
      });
    });
  });

  // Application form Super Admin approve button
  const formApproveBtn = document.getElementById('approveIssuePassBtn');
  if (formApproveBtn) {
    const parentForm = formApproveBtn.closest('form');
    if (parentForm) {
      parentForm.addEventListener('submit', function(e) {
        if (e.submitter && e.submitter.value === 'approve') {
          setTimeout(() => {
            formApproveBtn.disabled = true;
            formApproveBtn.innerHTML = '⏳ Approving &amp; Issuing Pass...';
            formApproveBtn.style.opacity = '0.7';
            formApproveBtn.style.cursor = 'not-allowed';
          }, 10);
        }
      });
    }
  }
}

function showApprovalToast(msg) {
  let toast = document.getElementById('adminApprovalToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'adminApprovalToast';
    toast.style.cssText = 'position: fixed; bottom: 24px; right: 24px; background: #065F46; color: #FFFFFF; padding: 12px 20px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); font-weight: 600; font-size: 0.9rem; z-index: 99999; display: flex; align-items: center; gap: 8px; border: 1.5px solid #10B981; animation: fadeIn 0.3s ease;';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<span>✓</span> <span>${msg}</span>`;
  toast.style.display = 'flex';
  setTimeout(() => {
    toast.style.display = 'none';
  }, 4500);
}
