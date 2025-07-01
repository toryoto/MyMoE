document.addEventListener('DOMContentLoaded', function() {
    console.log('Profile form JS loaded');
    
    const skillInput = document.getElementById('skill-input');
    const skillSuggestions = document.getElementById('skill-suggestions');
    const selectedSkillsContainer = document.getElementById('selected-skills');
    const skillsHiddenContainer = document.getElementById('skills-hidden-container');
    const originalSkillsField = document.querySelector('select[name="skills"]') || 
                                document.querySelector('input[name="skills"]') ||
                                document.querySelector('[name="skills"]');

    console.log('Elements found:', {
        skillInput: !!skillInput,
        skillSuggestions: !!skillSuggestions,
        selectedSkillsContainer: !!selectedSkillsContainer,
        skillsHiddenContainer: !!skillsHiddenContainer,
        originalSkillsField: !!originalSkillsField
    });

    let allSkills = [];
    let selectedSkillIds = new Set();

    // 元のフォームフィールドを無効化
    function disableOriginalField() {
        if (originalSkillsField) {
            originalSkillsField.disabled = true;
            originalSkillsField.style.display = 'none';
            
            // MultipleHiddenInputの場合、すべて無効化
            const allOriginalInputs = document.querySelectorAll('input[name="skills"]:not([id^="skill-hidden-"])');
            allOriginalInputs.forEach(input => {
                if (!input.id.startsWith('skill-hidden-')) {
                    input.disabled = true;
                }
            });
        }
    }

    // hidden inputを更新
    function updateHiddenInput() {
        // 既存のカスタムhidden inputを削除
        const existingInputs = skillsHiddenContainer.querySelectorAll('input[id^="skill-hidden-"]');
        existingInputs.forEach(input => input.remove());

        // 新しいhidden inputを作成
        selectedSkillIds.forEach((id, index) => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'skills';
            input.id = `skill-hidden-${index}`;
            input.value = id;
            skillsHiddenContainer.appendChild(input);
        });

        console.log('Updated hidden inputs. Total:', selectedSkillIds.size);
        console.log('Hidden input values:', Array.from(selectedSkillIds));
    }

    // スキルタグを追加
    function addSkillTag(name, id, shouldUpdate = true) {
        const skillId = parseInt(id);
        if (selectedSkillIds.has(skillId)) return;

        selectedSkillIds.add(skillId);

        const tag = document.createElement('span');
        tag.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800 border border-primary-200';
        tag.dataset.skillId = skillId;
        
        const nameSpan = document.createElement('span');
        nameSpan.textContent = name;
        
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'ml-2 inline-flex items-center justify-center w-4 h-4 rounded-full hover:bg-primary-200 focus:outline-none focus:bg-primary-200 transition-colors';
        removeBtn.innerHTML = '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>';
        removeBtn.setAttribute('aria-label', 'スキルを削除');
        
        removeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log(`Removing skill ID: ${skillId}`);
            selectedSkillIds.delete(skillId);
            tag.remove();
            updateHiddenInput();
            console.log('Current selected skills after removal:', Array.from(selectedSkillIds));
        });

        tag.appendChild(nameSpan);
        tag.appendChild(removeBtn);
        selectedSkillsContainer.appendChild(tag);
        
        if (shouldUpdate) {
            updateHiddenInput();
        }
    }

    // 初期化
    function initializeSkills() {
        console.log('Initializing skills...');
        
        // 元のフィールドを無効化
        disableOriginalField();
        
        // コンテナをクリア
        selectedSkillsContainer.innerHTML = '';
        skillsHiddenContainer.innerHTML = '';
        selectedSkillIds.clear();

        const initialSkillsElement = document.getElementById('initial-skills');
        console.log('Initial skills element:', !!initialSkillsElement);
        
        if (!initialSkillsElement) {
            console.error('initial-skills element not found');
            return;
        }
        
        const initialSkillIds = JSON.parse(initialSkillsElement.textContent);
        console.log('Initial skill IDs:', initialSkillIds);
        
        if (initialSkillIds && initialSkillIds.length > 0) {
            fetch(`/profiles/api/skills/search/`)
                .then(response => {
                    console.log('Skills API response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('All skills loaded:', data.length);
                    allSkills = data;
                    initialSkillIds.forEach(skillId => {
                        const skill = allSkills.find(s => s.id === parseInt(skillId));
                        if (skill) {
                            console.log('Adding initial skill:', skill.name);
                            addSkillTag(skill.name, skill.id, false);
                        } else {
                            console.warn('Skill not found for ID:', skillId);
                        }
                    });
                    updateHiddenInput();
                })
                .catch(error => {
                    console.error('Error loading initial skills:', error);
                });
        } else {
            console.log('No initial skills, loading all skills...');
            fetch(`/profiles/api/skills/search/`)
                .then(response => {
                    console.log('Skills API response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('All skills loaded:', data.length);
                    allSkills = data;
                })
                .catch(error => {
                    console.error('Error loading skills:', error);
                });
        }
    }

    // スキル検索
    if (skillInput) {
        skillInput.addEventListener('input', function() {
            const query = skillInput.value;
            console.log('Skill input query:', query);
            
            if (query.length < 1) {
                skillSuggestions.innerHTML = '';
                return;
            }

            fetch(`/profiles/api/skills/search/?q=${query}`)
                .then(response => {
                    console.log('Search API response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('Search results:', data);
                    allSkills = [...allSkills, ...data.filter(newSkill => 
                        !allSkills.some(existingSkill => existingSkill.id === newSkill.id)
                    )];
                    skillSuggestions.innerHTML = '';
                    data.forEach(skill => {
                        const option = document.createElement('option');
                        option.value = skill.name;
                        option.dataset.id = skill.id;
                        skillSuggestions.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching skills:', error);
                });
        });

        // Enterキーでスキル追加
        skillInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                const skillName = skillInput.value.trim();
                console.log('Enter pressed with skill name:', skillName);
                
                if (!skillName) return;
                
                const skill = allSkills.find(s => s.name.toLowerCase() === skillName.toLowerCase());
                console.log('Found skill:', skill);

                if (skill) {
                    addSkillTag(skill.name, skill.id);
                    skillInput.value = '';
                    skillSuggestions.innerHTML = '';
                } else {
                    console.warn('Skill not found in allSkills array');
                }
            }
        });
    } else {
        console.error('Skill input element not found');
    }

    // フォーム送信前の最終チェック
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // 元のフィールドが無効化されていることを確認
            disableOriginalField();
            
            console.log('=== フォーム送信時の状態 ===');
            console.log('Selected skills:', Array.from(selectedSkillIds));
            console.log('Hidden inputs:', skillsHiddenContainer.querySelectorAll('input').length);
            
            // FormDataで確認
            const formData = new FormData(form);
            console.log('FormData skills:', formData.getAll('skills'));
        });
    }

    // 初期化実行
    if (selectedSkillsContainer && skillsHiddenContainer) {
        console.log('Initializing skills system...');
        initializeSkills();
    } else {
        console.error('Required skill containers not found');
    }

    // 写真アップロード処理
    const photoInput = document.querySelector('input[type="file"][name="photo"]');
    const photoPreview = document.getElementById('photo-preview');
    const clearPhotoButton = document.getElementById('clear-photo');

    if (photoInput) {
        photoInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    photoPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (clearPhotoButton) {
        clearPhotoButton.addEventListener('click', function() {
            photoInput.value = '';
            // デフォルト画像のパスを動的に取得（複数のパターンに対応）
            const defaultImg = document.querySelector('img[alt*="デフォルト"]') || 
                             document.querySelector('img[src*="default_profile"]') ||
                             document.querySelector('#photo-preview');
            
            if (defaultImg && defaultImg.src.includes('default_profile')) {
                photoPreview.src = defaultImg.src;
            } else {
                // フォールバック: 既存の画像のsrcからdefault画像のパスを推定
                const currentSrc = photoPreview.src;
                const basePath = currentSrc.substring(0, currentSrc.lastIndexOf('/') + 1);
                photoPreview.src = basePath + 'default_profile.png';
            }
            
            const clearCheckbox = document.getElementById('photo-clear_id');
            if (clearCheckbox) {
                clearCheckbox.checked = true;
            }
            clearPhotoButton.style.display = 'none';
        });
    }

    // 履歴フォーム処理
    const addFormButton = document.getElementById('add-history-form');
    const formsContainer = document.getElementById('history-forms-container');
    const emptyForm = document.getElementById('empty-form');
    const totalFormsInput = document.querySelector('input[name="history-TOTAL_FORMS"]');

    if (addFormButton && formsContainer && totalFormsInput && emptyForm) {
        addFormButton.addEventListener('click', function() {
            const formNum = parseInt(totalFormsInput.value);
            const newForm = emptyForm.innerHTML.replace(/__prefix__/g, formNum);
            formsContainer.insertAdjacentHTML('beforeend', newForm);
            totalFormsInput.value = formNum + 1;
        });
    }
});
