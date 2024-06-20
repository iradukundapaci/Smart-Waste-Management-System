from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import db, Schedule, UpcomingCollection
from app.forms import ScheduleForm, GenerateCollectionsForm

user_bp = Blueprint("user", __name__)


@user_bp.route("/schedule", methods=["GET", "POST"])
@login_required
def schedule():
    form = ScheduleForm()
    generate_form = GenerateCollectionsForm()

    if form.validate_on_submit():
        existing_schedule = Schedule.query.filter_by(
            user_id=current_user.id, day_of_week=form.day_of_week.data
        ).first()
        if existing_schedule:
            flash("Schedule for this day already exists.", "danger")
        else:
            schedule = Schedule(
                user_id=current_user.id, day_of_week=form.day_of_week.data
            )
            db.session.add(schedule)
            db.session.commit()
            flash("Schedule day added successfully.", "success")
        return redirect(url_for("user.schedule"))

    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    upcoming_collections = UpcomingCollection.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "schedule.html",
        schedules=schedules,
        form=form,
        generate_form=generate_form,
        upcoming_collections=upcoming_collections,
    )


@user_bp.route("/schedule/generate", methods=["POST"])
@login_required
def generate_collections():
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    for schedule in schedules:
        next_date = next_weekday(datetime.now(), schedule.day_of_week)
        existing_collection = UpcomingCollection.query.filter_by(
            user_id=current_user.id, collection_date=next_date
        ).first()
        if not existing_collection:
            collection = UpcomingCollection(
                user_id=current_user.id, collection_date=next_date
            )
            db.session.add(collection)

    db.session.commit()
    flash("Upcoming collections generated successfully.", "success")
    return redirect(url_for("user.schedule"))


@user_bp.route("/schedule/<int:schedule_id>/edit", methods=["GET", "POST"])
@login_required
def edit_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if schedule.user_id != current_user.id:
        flash("You do not have permission to edit this schedule.", "danger")
        return redirect(url_for("user.schedule"))

    form = ScheduleForm(obj=schedule)
    if form.validate_on_submit():
        schedule.day_of_week = form.day_of_week.data
        db.session.commit()
        flash("Schedule updated successfully.", "success")
        return redirect(url_for("user.schedule"))
    return render_template("edit_schedule.html", form=form, schedule=schedule)


@user_bp.route("/schedule/<int:schedule_id>/delete", methods=["Get"])
@login_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if schedule.user_id != current_user.id:
        flash("You do not have permission to delete this schedule.", "danger")
        return redirect(url_for("user.schedule"))

    db.session.delete(schedule)
    db.session.commit()
    flash("Schedule deleted successfully.", "success")
    return redirect(url_for("user.schedule"))


@user_bp.route("/collection/<int:collection_id>/delete", methods=["POST"])
@login_required
def delete_collection(collection_id):
    collection = UpcomingCollection.query.get_or_404(collection_id)
    if collection.user_id != current_user.id:
        flash("You do not have permission to delete this collection.", "danger")
        return redirect(url_for("user.schedule"))

    db.session.delete(collection)
    db.session.commit()
    flash("Collection deleted successfully.", "success")
    return redirect(url_for("user.schedule"))


def next_weekday(d, day_name):
    days_of_week = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    days_ahead = days_of_week.index(day_name) - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days_ahead)
