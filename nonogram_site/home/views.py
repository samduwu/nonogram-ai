### import OpenCV and numpy
import cv2
import numpy as np

from django.shortcuts import render
from django.http import HttpResponse

# Instructs whether to save real contours or not to final result
TESTING = False

# Utility functions

# Sorts contours from bottom to top AND right to left
def sort_contours_grouped(contours, y_thresh=10): # thresh might need to change for different sizes
  bounding_boxes = [cv2.boundingRect(c) for c in contours]

  # Sort all contours top-to-bottom first
  cnts_bboxes = sorted(zip(contours, bounding_boxes), key=lambda b: b[1][1])

  rows = []
  current_row = []
  last_y = None

  for cnt, box in cnts_bboxes:
    if last_y is None:
      current_row.append((cnt, box))
      last_y = box[1]
    else:
      # Check if current contour is within the y_thresh of the current row
      if abs(box[1] - last_y) <= y_thresh:
        current_row.append((cnt, box))
      else:
        # Sort current row from right to left (x descending)
        current_row.sort(key=lambda b: b[1][0], reverse=True)
        rows.append(current_row)
        current_row = [(cnt, box)]
        last_y = box[1]

  if current_row:
    current_row.sort(key=lambda b: b[1][0], reverse=True)
    rows.append(current_row)

  # Now reverse the rows list so the bottom row comes first (bottom-to-top)
  rows.reverse()

  # rows[i] - list of all contours in the row
  # rows[i][0][0] - specific contour info
  # rows[i][0][1] - bounding box info for that contour
  return rows

# DOUBLE DIGIT LOGIC (might be naive)
def is_double(x, next_x, next_w, near_tolerance=10):
    double_detected = False

    # If the right hand border of the left (next) number is within the tolerance of the right (current) number's left border
    if abs((next_x + next_w) - x) < near_tolerance:
        double_detected = True
    return double_detected


def position_column_values(column_values):
  # Ensure that we don't hit index error if expected row length appears
  if len(column_values) == 1:
    return column_values

  x_positions = []
  column_len = len(column_values)
  column_dimension = len(column_values[-1])

  return_list = []

  # Copy just the contour info into the final list
  filled_row = []
  for contour_info in column_values[-1]:
    if isinstance(contour_info, list):
      filled_row.append([contour_info[0][0], contour_info[1][0]])
    else:
      filled_row.append(contour_info[0])

  return_list.append(filled_row)

  # Track x-coord of each number on the full row of column values
  for contour in column_values[-1]:
    # Handle any double digits in the first row
    if isinstance(contour, list):
      # contour is
      # [
      #   (
      #     (contour - np.array, bounding_box - tuple of len4),
      #     (contour2 - np.array, bounding_box2 - tuple of len4),
      #   )
      # ]
      x = (contour[0][1][0] + contour[1][1][0]) // 2
    else:
      x = contour[1][0]
    x_positions.append(x)

  print(f'this is x_values: {x_positions}')

  # Index backwards from the 2nd to last row, and continue upward
  for row_idx in range(column_len - 2, -1, -1):
    print(f'starting row {row_idx}')

    # List to put contour with 0s in
    column_list_horizontal = []
    current_item_idx = 0

    # Index through each item in the row
    for contour_idx in range(len(column_values[row_idx])):
      is_double = False
      print(f'starting iteam {contour_idx}')

      # Check if we have a double digit - represented by a list(Ex: [digit1, digit2])
      if isinstance(column_values[row_idx][contour_idx], list):
        # Average the x values
        x_coord = (column_values[row_idx][contour_idx][0][1][0] + column_values[row_idx][contour_idx][1][1][0]) // 2
        is_double = True
      else:
        x_coord = column_values[row_idx][contour_idx][1][0]

      print(row_idx, contour_idx)
      print(x_positions)

      # Find closest value that exists in x_positions
      closest_value = min(x_positions, key=lambda value: abs(value - x_coord))

      # Use the idx from x_positions to see where it should go positionally
      closest_idx = x_positions.index(closest_value)
      print(f'x-coord {x_coord} and closest_idx {closest_idx}')
      if closest_idx == current_item_idx:
        # Item is already in the correct place
        if not TESTING:
          if is_double:
            print(column_values[row_idx][contour_idx])
            column_list_horizontal.append([column_values[row_idx][contour_idx][0][0], column_values[row_idx][contour_idx][1][0]])
          else:
            column_list_horizontal.append(column_values[row_idx][contour_idx][0])
        else:
          column_list_horizontal.append('contour in place')
        current_item_idx += 1
      else:
        # Otherwise, insert 0s as needed
        number_of_zeros = abs(closest_idx - current_item_idx)
        print(f"Adding {number_of_zeros} zeros")
        for i in range(number_of_zeros):
          column_list_horizontal.insert(current_item_idx, 0)

        if not TESTING:
          if is_double:
            column_list_horizontal.append([column_values[row_idx][contour_idx][0][0], column_values[row_idx][contour_idx][1][0]])
          else:
            column_list_horizontal.append(column_values[row_idx][contour_idx][0])
        else:
          column_list_horizontal.append('contour')
        current_item_idx = closest_idx + 1

    # Add padding to the right of the list if there is no final column value
    if current_item_idx != column_dimension:
      # Because we add 1 to the current_item_idx each loop, we are 1 index above the last change
      column_list_horizontal.extend([0] * abs(column_dimension - current_item_idx))

    # Insert the generated list to the final return list
    return_list.insert(0, column_list_horizontal)

  return return_list

# Create your views here.
def index(request):
    return render(request, "home/landing.html",  {})

def process(request):
    if request.method == "POST":
        upload = request.FILES.get("nonogram")
        print('got here')
        
        if upload:
            # TODO: add try except here
            # We cannot read in the image from memory since OpenCV expects a static path, so we encode it as a numpy array first
            # Read the raw bytes from the uploaded file
            file_bytes = np.frombuffer(upload.read(), np.uint8)

            # Decode the bytes into an OpenCV BGR image matrix (This is equivalent to cv2.imread)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if image is None:
                # Handle bad image files or unsupported formats
                HttpResponse("Unable to process image.")

            height, width, channels = image.shape
            print(f"Height: {height}, Width: {width}, Channels: {channels}")

            # Resizing image. This multiplies the size by 3. Might be too much or might be
            # possible with smaller size, but not sure
            resized_image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

            # Kernel matrix
            kernel = np.ones((3,3), np.uint8)

            # Dilate the image. This expands the white regions of the image
            # Done to get rid of small lines connecting double digit numbers
            img_dilate = cv2.dilate(resized_image, kernel, iterations=1)

            # Kernel matrix for doing erosion
            kernel_opp = np.ones((2,2), np.uint8)

            # Erode the image (helps isolate small numbers in double digit numbers)
            img_erosion = cv2.erode(img_dilate, kernel_opp, iterations=1)

            # Convert image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Inverts the color of the items, since we want our items of note to be white
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

            # Find contours
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # TODO: Could add some way to display image processing progress so far (cv2.imshow)

            # Remove extraneous contour information
            number_contours = []
            h_list = hierarchy[0]

            # Using the area of a small square to get rid of large contours that don't disappear through the parent/child filter
            square_area = cv2.contourArea(contours[1])

            for idx, contour in enumerate(contours):
                nxt, prev, child, parent = h_list[idx]
                if parent != -1:
                    # Get rid of lines
                    if cv2.contourArea(contour) < square_area:
                        # remove unnecessary dimension that has len 1
                        #i.e. (2,1,2) -> (2,2)
                        if not child != -1:
                            if not h_list[parent][3] != 0:
                                number_contours.append(contour.squeeze())
                        else:
                            number_contours.append(contour.squeeze())

            # TODO: Could add some way to display image processing progress so far (cv2.imshow)

            ### Sort contours from bottom to top; right to left
            # Each item in rows is a list of each number of rows;
            # removes the need to detect when we shift to column values
            # EX: [[1, 3, 1], [1, 7], [9]]
            # ->
            # [
            #  [(contour_info_1, (x, y, w, h)), (contour_info_2, (x2, y2, w2, h2)), (...)],
            #  [(contour_info_4, (x4, y4, w4, h4), (...)],
            #  [(contour_info_5, (x5, y5, w5, h5), (...)],
            # ]
            rows = sort_contours_grouped(number_contours, 10)

            ### Separate rows data into row and column lists

            pixel_tolerance = 20 # pixel tolerance for determining if we have shifted to looking at column values
            starting_x = None # keeps track of the first number we add to our list, so we know when we have shifted to reading the column values
            track_columns = False # flag to track whether we should add to rows or columns list

            # lists to hold positional items
            row_values = []
            column_values = []

            # General loop through all contours (iterable so we can skip contours for double digits)
            iterator = iter(enumerate(rows))
            for index, row in iterator:
                print(f'evaluating index {index}')
                iter_row = iter(enumerate(row))
                if track_columns:
                    column_values.insert(0, [])
                else:
                    row_values.insert(0, [])
                for contour_index, contour_info in iter_row:
                    next_contour_info = None
                    print(f'evaluating contour_index {contour_index}')
                    next_contour = None
                    box = contour_info[1]
                    contour = contour_info[0]
                    is_double_digit = False

                    # Ensure there is a next item before checking double_digit
                    if contour_index < len(row) - 1:
                        next_contour_info = row[contour_index + 1]

                    x, y, = box[0], box[1]

                    # Set the value for our starting column (x-coord)
                    if starting_x is None:
                        starting_x = box[0]

                    # Determine if we have shifted to the column values
                    # Check if we are not in range, and the column value is greater than start
                    elif starting_x is not None and (abs(x - starting_x) > pixel_tolerance) and (x > starting_x):
                        track_columns = True
                        column_values.insert(0, [])
                        starting_x = x

                    # Only do double digit check if there is a future element
                    if next_contour_info:
                        next_box = next_contour_info[1]
                        next_contour = next_contour_info[0]
                        next_x, next_w, = next_box[0], next_box[2]

                        double_digit_check = is_double(x, next_x, next_w, near_tolerance=10)
                        if double_digit_check:
                            print('we have double digit')
                            # update the most recent value to be a list
                            is_double_digit = True

                    # add the value to the newest list
                    if is_double_digit:
                        if track_columns:
                            column_values[0].insert(0, [(next_contour, next_box), (contour, box)] if not TESTING else ["digit1", "digit2"])
                        else:
                            row_values[0].insert(0, [next_contour, contour] if not TESTING else ["digit1", "digit2"])
                        if is_double_digit:
                            skip = next(iter_row, None)  # skip the next contour if we had a double digit
                    else:
                        if track_columns:
                            column_values[0].insert(0, (contour, box) if not TESTING else "num")
                        else:
                            row_values[0].insert(0, contour if not TESTING else "num")

            # Clean empty lists from either result
            final_row_values = [x for x in row_values if x != []]
            clean_column_values = column_values
            del column_values

            ### Position column values
            final_column_values = position_column_values(clean_column_values)

            print(final_row_values)
            print(final_column_values)
            return HttpResponse("working!")

            # TODO: Figure out how to extract original image from contour
            # TODO: Put AI prediction here (Could separate into another view afterward)

        else:
            return HttpResponse("No image uploaded.")
    else:
        return HttpResponse("Unable to process non-POST request.")
