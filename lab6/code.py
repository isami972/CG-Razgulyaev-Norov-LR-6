import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import math
import os
import numpy as np


class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Геометрические преобразования - Вариант 16")
        self.root.geometry("1400x700")

        self.original_image = None
        self.affine_result = None
        self.inverse_affine_result = None
        self.functional_result = None

        self.create_widgets()

    def create_widgets(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        btn_load = tk.Button(control_frame, text="Загрузить изображение", command=self.load_image)
        btn_load.pack(side=tk.LEFT, padx=5)

        affine_frame = tk.LabelFrame(control_frame, text="Аффинные преобразования (Скос + Отражение)")
        affine_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(affine_frame, text="Коэффициент скоса:").grid(row=0, column=0, padx=5)
        self.skew_param_var = tk.StringVar(value="0.3")
        skew_entry = tk.Entry(affine_frame, textvariable=self.skew_param_var, width=8)
        skew_entry.grid(row=0, column=1, padx=5)

        btn_affine = tk.Button(affine_frame, text="Применить скос+отражение", 
                              command=self.apply_affine_transform)
        btn_affine.grid(row=1, column=0, columnspan=2, pady=5)

        btn_inverse_affine = tk.Button(affine_frame, text="Восстановить обратным", 
                                      command=self.apply_inverse_affine)
        btn_inverse_affine.grid(row=2, column=0, columnspan=2, pady=5)

        func_frame = tk.LabelFrame(control_frame, text="Функциональное преобразование")
        func_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(func_frame, text="i = ln(x'), j = y'").grid(row=0, column=0, columnspan=2, padx=5)
        
        btn_functional = tk.Button(func_frame, text="Применить ln-преобразование", 
                                  command=self.apply_functional_transform)
        btn_functional.grid(row=1, column=0, columnspan=2, pady=5)

        save_frame = tk.LabelFrame(control_frame, text="Сохранение")
        save_frame.pack(side=tk.LEFT, padx=10)

        btn_save_all = tk.Button(save_frame, text="Сохранить все в PNG и PPM",
                                 command=self.save_all_formats)
        btn_save_all.pack(pady=10, padx=10)

        display_frame = tk.Frame(self.root)
        display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        orig_frame = tk.LabelFrame(display_frame, text="Оригинальное изображение")
        orig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.original_label = tk.Label(orig_frame)
        self.original_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        affine_frame_display = tk.LabelFrame(display_frame, text="Скос+Отражение")
        affine_frame_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.affine_label = tk.Label(affine_frame_display)
        self.affine_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        inverse_frame = tk.LabelFrame(display_frame, text="Восстановленное")
        inverse_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.inverse_label = tk.Label(inverse_frame)
        self.inverse_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        func_frame_display = tk.LabelFrame(display_frame, text="ln(x') преобразование")
        func_frame_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.functional_label = tk.Label(func_frame_display)
        self.functional_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.ppm")]
        )
        if file_path:
            try:
                self.original_image = Image.open(file_path).convert('RGB')
                self.display_image(self.original_image, self.original_label)
                
                self.affine_result = None
                self.inverse_affine_result = None
                self.functional_result = None
                
                self.clear_result_displays()
                messagebox.showinfo("Успех", "Изображение успешно загружено")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")

    def clear_result_displays(self):
        for label in [self.affine_label, self.inverse_label, self.functional_label]:
            label.config(image='', text="Нет изображения")

    def display_image(self, image, label):
        if image is None:
            label.config(image='', text="Нет изображения")
            return

        display_size = (250, 250)
        image_copy = image.copy()
        
        # Убрать Image.Resampling - используем простой thumbnail
        image_copy.thumbnail(display_size)

        photo = ImageTk.PhotoImage(image_copy)
        label.config(image=photo, text="")
        label.image = photo

    def apply_affine_transform(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        try:
            skew_factor = float(self.skew_param_var.get())
            width, height = self.original_image.size
            
            # Создаем увеличенное изображение для результата
            new_width = int(width * 1.5)
            new_height = int(height * 1.5)
            result = Image.new('RGB', (new_width, new_height), (255, 255, 255))
            
            # Преобразование: скос по X и отражение по Y
            # Прямое преобразование: i = x + k*y, j = -y + height (отражение)
            
            for x in range(new_width):
                for y in range(new_height):
                    # Обратное отображение для избежания пропусков
                    x_orig = x - skew_factor * y
                    y_orig = height - y
                    
                    x_orig = int(x_orig)
                    y_orig = int(y_orig)
                    
                    if 0 <= x_orig < width and 0 <= y_orig < height:
                        pixel = self.original_image.getpixel((x_orig, y_orig))
                        result.putpixel((x, y), pixel)
            
            self.affine_result = result
            self.display_image(result, self.affine_label)
            messagebox.showinfo("Успех", "Скос и отражение применены успешно")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение параметра скоса")

    def apply_inverse_affine(self):
        if self.affine_result is None:
            messagebox.showwarning("Предупреждение", "Сначала примените прямое преобразование")
            return

        try:
            skew_factor = float(self.skew_param_var.get())
            width, height = self.affine_result.size
            orig_width, orig_height = self.original_image.size
            
            # Восстановление обратным преобразованием
            result = Image.new('RGB', (orig_width, orig_height), (255, 255, 255))
            
            for x in range(orig_width):
                for y in range(orig_height):
                    # Обратное преобразование: x' = x + k*(orig_height - y), y' = orig_height - y
                    x_affine = x + skew_factor * (orig_height - y)
                    y_affine = orig_height - y
                    
                    x_affine = int(x_affine)
                    y_affine = int(y_affine)
                    
                    if 0 <= x_affine < width and 0 <= y_affine < height:
                        pixel = self.affine_result.getpixel((x_affine, y_affine))
                        result.putpixel((x, y), pixel)
            
            self.inverse_affine_result = result
            self.display_image(result, self.inverse_label)
            messagebox.showinfo("Успех", "Восстановление обратным преобразованием выполнено")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при восстановлении: {str(e)}")

    def apply_functional_transform(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        try:
            width, height = self.original_image.size
            
            # Создаем изображение для результата
            result = Image.new('RGB', (width, height), (255, 255, 255))
            
            # Функциональное преобразование для варианта 16: i = ln(x'), j = y'
            # Используем обратное отображение
            
            if width > 0:
                max_log_val = math.log(width)
            else:
                max_log_val = 1
            
            for x in range(width):
                for y in range(height):
                    try:
                        # Обратное преобразование: x' = exp(x_scaled)
                        x_scaled = x * (max_log_val / width) if width > 0 else 0
                        x_orig = math.exp(x_scaled)
                        
                        # Ограничиваем в пределах исходного изображения
                        x_orig = min(int(x_orig), width - 1)
                        y_orig = min(y, height - 1)
                        
                        if 0 <= x_orig < width and 0 <= y_orig < height:
                            pixel = self.original_image.getpixel((x_orig, y_orig))
                            result.putpixel((x, y), pixel)
                    except (ValueError, OverflowError):
                        continue
            
            self.functional_result = result
            self.display_image(result, self.functional_label)
            messagebox.showinfo("Успех", "Логарифмическое преобразование применено")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при преобразовании: {str(e)}")

    def save_all_formats(self):
        images_to_save = [
            ("skew_reflection", self.affine_result),
            ("restored", self.inverse_affine_result),
            ("log_transform", self.functional_result)
        ]

        available_images = [(name, image) for name, image in images_to_save if image is not None]

        if not available_images:
            messagebox.showwarning("Предупреждение", "Нет изображений для сохранения")
            return

        folder_path = filedialog.askdirectory(title="Выберите папку для сохранения")

        if not folder_path:
            return

        saved_files = []
        
        for name, image in available_images:
            try:
                # Сохраняем в PNG
                png_path = os.path.join(folder_path, f"{name}.png")
                image.save(png_path, "PNG")
                saved_files.append(f"{name}.png")
                
                # Сохраняем в PPM
                ppm_path = os.path.join(folder_path, f"{name}.ppm")
                image.save(ppm_path, "PPM")
                saved_files.append(f"{name}.ppm")
                
            except Exception as e:
                continue

        if saved_files:
            messagebox.showinfo("Успех", f"Сохранено файлов: {len(saved_files)}\n{chr(10).join(saved_files)}")
        else:
            messagebox.showwarning("Предупреждение", "Не удалось сохранить файлы")


def main():
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()


if __name__ == "__main__":
    main()