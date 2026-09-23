document.addEventListener("DOMContentLoaded", () => {
  const menuButton = document.querySelector(".mobile-menu-button, [data-menu-button]");
  const navigation = document.querySelector(".main-navigation, [data-navigation]");

  if (menuButton && navigation) {
    menuButton.addEventListener("click", () => {
      const isOpen = navigation.classList.toggle("open");
      menuButton.classList.toggle("active", isOpen);
      menuButton.setAttribute("aria-expanded", String(isOpen));
    });

    navigation.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        navigation.classList.remove("open");
        menuButton.classList.remove("active");
        menuButton.setAttribute("aria-expanded", "false");
      });
    });
  }

  document.querySelectorAll("[data-message], .message").forEach((message) => {
    const closeButton = message.querySelector("[data-message-close], .message-close");
    if (closeButton) closeButton.addEventListener("click", () => message.remove());
  });

  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach((input) => {
    input.addEventListener("change", () => {
      const parent = input.closest(".file-upload-area");
      const label = parent?.querySelector("p");
      if (label && input.files.length) label.textContent = input.files[0].name;
    });
  });

  document.querySelectorAll('textarea[maxlength], input[maxlength]').forEach((field) => {
    const counter = document.createElement("small");
    counter.className = "character-counter";
    field.insertAdjacentElement("afterend", counter);
    const update = () => { counter.textContent = `${field.value.length}/${field.maxLength}`; };
    field.addEventListener("input", update);
    update();
  });
});
